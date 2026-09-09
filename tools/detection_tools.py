"""Detection-engineering tools: Sigma, YARA and Suricata.

Why these are tools and not just `terminal` calls
-------------------------------------------------
The agent can already shell out to `sigma`, `yara` and `suricata` through the
terminal toolset, so on capability grounds this module is redundant. It exists
for three things terminal access does not give:

1. **Dependency gating.** Each toolset declares a ``check_fn`` that looks for
   its binary. When the binary is absent the tool is not offered at all, and
   `socis doctor` reports "system dependency not met". Without that the agent
   discovers the gap by running a command that fails, and — worse — a skill
   whose central claim is "a rule you have not tested is not finished" can
   quietly skip the testing step and present an unvalidated rule as done.

2. **Structured arguments instead of constructed shell.** The agent passes a
   rule as a string and a path as a path; this module builds the argv list.
   Nothing reaches a shell, so there is no quoting to get wrong and no command
   injection surface from rule text that legitimately contains quotes, `$`,
   backticks and newlines — which YARA and Sigma rules routinely do.

3. **Per-toolset enable/disable.** A detection engineer working in Splunk may
   never touch YARA. Three toolsets rather than one lets them enable only what
   they use, and keeps the tool list short for everyone else.

Design notes
------------
- Every subprocess call uses a list argv with ``shell=False`` and a timeout.
- Rule text is written to a temp file under the process's own temp directory,
  never to a caller-supplied path.
- Output is truncated: a YARA scan of a large tree can emit megabytes, and an
  unbounded tool result is a context-window problem.
- Nothing here writes to a customer's environment. These tools validate and
  test locally; deployment stays a deliberate human action.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from tools.registry import registry

logger = logging.getLogger(__name__)

# A rule that takes longer than this to compile or run against a sample set is
# almost certainly pathological (unbounded regex, scanning a mounted share).
# Failing with a clear timeout beats hanging a session.
_TIMEOUT = 120
_MAX_OUTPUT = 20_000


def _run(argv: list[str], *, cwd: Optional[str] = None, timeout: int = _TIMEOUT) -> dict:
    """Run *argv* with no shell, bounded time and bounded output."""
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
    except FileNotFoundError:
        return {"ok": False, "error": f"{argv[0]} not found on PATH."}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"{argv[0]} exceeded {timeout}s and was terminated."}

    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    truncated = False
    if len(out) > _MAX_OUTPUT:
        out = out[:_MAX_OUTPUT]
        truncated = True
    return {
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stdout": out,
        "stderr": err[:_MAX_OUTPUT],
        "truncated": truncated,
    }


def _write_temp(content: str, suffix: str) -> str:
    """Write *content* to a temp file and return its path.

    Caller-supplied paths are never written to — a tool that accepts both rule
    text and an output path is one prompt-injection away from writing attacker
    content wherever the agent has permission.
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="socis-detect-")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def _fmt(result: dict, *, on_success: str) -> str:
    if result.get("error"):
        return f"❌ {result['error']}"
    if result["ok"]:
        body = result["stdout"] or on_success
        return f"✅ {body}" + ("\n\n[output truncated]" if result.get("truncated") else "")
    detail = result["stderr"] or result["stdout"] or f"exit {result['exit_code']}"
    return f"❌ Failed:\n{detail}"


# ── Sigma ────────────────────────────────────────────────────────────────────

def _sigma_check() -> bool:
    return shutil.which("sigma") is not None


def _handle_sigma_check(args: dict, **_kw) -> str:
    rule = args.get("rule") or ""
    if not rule.strip():
        return "❌ `rule` is required (the Sigma YAML as text)."
    path = _write_temp(rule, ".yml")
    try:
        return _fmt(_run(["sigma", "check", path]),
                    on_success="Rule is valid Sigma.")
    finally:
        Path(path).unlink(missing_ok=True)


def _handle_sigma_list(args: dict, **_kw) -> str:
    """Discover what this installation can actually convert to.

    sigma-cli ships no backends by default — each SIEM is a separate pySigma
    package. So `sigma convert -t splunk` fails on a fresh install, and the
    agent has no way to know that without asking. This tool is the ask.
    """
    what = (args.get("what") or "targets").strip().lower()
    if what == "plugins":
        # Everything installable, not just what is present.
        res = _run(["sigma", "plugin", "list"])
        out = _fmt(res, on_success="(no output)")
        if res.get("ok"):
            out += ("\n\nInstall a backend with `sigma plugin install <identifier>`. "
                    "SOCIS does not run that for you — installing a package is a "
                    "supply-chain decision a human should make deliberately.")
        return out
    if what == "formats":
        backend = args.get("backend") or ""
        if not backend.strip():
            return "❌ `backend` is required when listing formats."
        return _fmt(_run(["sigma", "list", "formats", backend]), on_success="(no output)")
    if what not in ("targets", "pipelines"):
        return "❌ `what` must be one of: targets, pipelines, plugins, formats."

    argv = ["sigma", "list", what]
    # Scope pipelines to a backend when one is given. `sigma list pipelines`
    # unscoped omits backend-specific pipelines — splunk_windows, splunk_cim
    # and splunk_sysmon_acceleration only appear under
    # `sigma list pipelines splunk`. Reading the unscoped output and concluding
    # a pipeline does not exist is exactly the mistake this argument prevents.
    backend = (args.get("backend") or "").strip()
    if what == "pipelines" and backend:
        argv.append(backend)

    res = _run(argv)
    out = _fmt(res, on_success="(no output)")
    if res.get("ok") and what == "targets" and not res["stdout"]:
        out += ("\n\n⚠ No targets installed. sigma-cli ships with no backends — each "
                "SIEM is a separate package. Run `sigma plugin list` to see what is "
                "available, then `sigma plugin install <backend>`.")
    return out


def _handle_sigma_convert(args: dict, **_kw) -> str:
    rule = args.get("rule") or ""
    target = args.get("target") or ""
    if not rule.strip() or not target.strip():
        return "❌ Both `rule` and `target` are required."

    path = _write_temp(rule, ".yml")
    argv = ["sigma", "convert", "-t", target]

    # Pipelines map Sigma's generic field names onto the target's real schema.
    # Several can apply at once, and sigma-cli applies -p in order.
    #
    # PIPELINES ARE BACKEND-SCOPED. `sigma list pipelines` with no argument
    # shows a different set from `sigma list pipelines splunk` — the latter is
    # the one that matters, and it is where splunk_windows, splunk_cim and
    # splunk_sysmon_acceleration appear. Reading the unscoped list and
    # concluding a pipeline is missing is an easy and costly mistake.
    #
    # Still: do not type a name from memory. Call sigma_list (what=pipelines,
    # backend=<target>) first. A name that is not installed fails the
    # conversion outright, which is the safe failure; naming a wrong but
    # installed pipeline produces a query that runs and matches nothing.
    pipelines = args.get("pipelines") or ([args["pipeline"]] if args.get("pipeline") else [])
    if isinstance(pipelines, str):
        pipelines = [pipelines]
    for pl in pipelines:
        if pl:
            argv += ["-p", str(pl)]

    # Some backends emit more than a bare query — Splunk can produce a
    # savedsearches.conf, others emit rule files for direct import. `sigma list
    # formats <backend>` enumerates them.
    fmt = args.get("format")
    if fmt:
        argv += ["-f", str(fmt)]

    argv.append(path)
    try:
        res = _run(argv)
        out = _fmt(res, on_success="(no output)")
        if res.get("ok") and not pipelines:
            out += ("\n\n⚠ No pipeline specified. Field names stay generic and may not "
                    "match your SIEM's schema — the query can be syntactically valid "
                    "and still never match anything. That is the most expensive kind "
                    "of wrong, because it looks like a working detection. Re-run with "
                    "`pipelines` set; `sigma_list` with what=pipelines shows the options.")
        if not res.get("ok") and "target" in (res.get("stderr") or "").lower():
            out += (f"\n\nThe `{target}` backend may not be installed. sigma-cli ships "
                    "with none by default. Check with `sigma_list` (what=targets), and "
                    "install via `sigma plugin install {target}`.")
        return out
    finally:
        Path(path).unlink(missing_ok=True)


# ── YARA ─────────────────────────────────────────────────────────────────────

def _yara_check() -> bool:
    return shutil.which("yara") is not None or shutil.which("yarac") is not None


def _resolve_rule_text(args: dict) -> tuple[str, str]:
    """Return ``(rule_text, error)`` from either ``rule`` or ``rule_file``.

    Callers naturally reach for the path of a rule they just wrote, and passing
    it as ``rule`` fed the PATH to yara as rule source: the failure surfaced as
    ``syntax error, unexpected regular expression`` on a temp file the caller
    never created — unattributable, and it pushed one agent into shelling out
    to raw `yara` instead, losing this tool's guardrails at the exact moment
    they mattered.

    Reading a caller-supplied path is safe; _write_temp's rule against
    caller-supplied paths is about WRITING to them.
    """
    text = (args.get("rule") or "").strip()
    ref = (args.get("rule_file") or "").strip()

    # A bare path handed to `rule` is the mistake this exists to catch.
    if text and not ref and "\n" not in text and len(text) < 4096:
        maybe = Path(text).expanduser()
        if maybe.suffix in (".yar", ".yara") and maybe.is_file():
            ref, text = str(maybe), ""

    if ref:
        f = Path(ref).expanduser()
        if not f.is_file():
            return "", f"❌ Rule file not found: {ref}"
        try:
            body = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return "", f"❌ Cannot read {ref}: {exc}"
        if not body.strip():
            return "", f"❌ Rule file is empty: {ref}"
        return body, ""

    if not text:
        # Name the key the caller actually sent. `yara_scan` takes `path` and
        # `yara_compile` does not, so `path` is the near-miss to expect — and
        # an error that lists only the valid names reads as "this tool is
        # broken": one agent abandoned the tool entirely and spent six turns
        # shelling out to raw `yara` rather than retrying with `rule_file`.
        known = {"rule", "rule_file", "path"}
        sent = [k for k in args if k not in ("rule", "rule_file") and args.get(k)]
        hint = ""
        for k in sent:
            v = args.get(k)
            if isinstance(v, str) and (v.endswith(".yar") or v.endswith(".yara")):
                hint = (f" You passed `{k}=\"{v}\"` — for a rule already on "
                        f"disk use `rule_file=\"{v}\"`.")
                break
        else:
            if sent:
                hint = (" Received: " + ", ".join(f"`{k}`" for k in sent)
                        + ". Unknown keys are ignored.")
        return "", ("❌ Provide `rule` (rule text) or `rule_file` (path to a "
                    ".yar file)." + hint)
    return text, ""


def _handle_yara_compile(args: dict, **_kw) -> str:
    rule, err = _resolve_rule_text(args)
    if err:
        return err
    rule_path = _write_temp(rule, ".yar")
    out_path = rule_path + ".yac"
    binary = "yarac" if shutil.which("yarac") else "yara"
    try:
        if binary == "yarac":
            res = _run([binary, rule_path, out_path])
        else:
            # `yara <rule> <empty dir>` compiles the rule and scans nothing.
            with tempfile.TemporaryDirectory() as empty:
                res = _run([binary, rule_path, empty])
        return _fmt(res, on_success="Rule compiles.")
    finally:
        Path(rule_path).unlink(missing_ok=True)
        Path(out_path).unlink(missing_ok=True)


def _handle_yara_scan(args: dict, **_kw) -> str:
    rule, err = _resolve_rule_text(args)
    if err:
        return err
    target = args.get("path") or ""
    if not target.strip():
        return "❌ `path` is required (what to scan)."
    if not Path(target).exists():
        return f"❌ Path does not exist: {target}"
    rule_path = _write_temp(rule, ".yar")
    try:
        # -s prints the matching strings, which is what makes a false positive
        # diagnosable rather than merely visible.
        res = _run(["yara", "-r", "-s", rule_path, target])
        if res.get("error"):
            return f"❌ {res['error']}"
        hits = res["stdout"]
        if res["ok"] and not hits:
            return (f"✅ No matches in {target}.\n\n"
                    "For a goodware corpus this is the result you want — zero hits "
                    "means no false positives here. For a sample set it means the "
                    "rule does not fire and needs work.")
        return _fmt(res, on_success="(no output)")
    finally:
        Path(rule_path).unlink(missing_ok=True)


def _yargen_db_home() -> Path:
    """Directory that owns yarGen's ``dbs/``.

    yarGen looks for ``dbs/`` under the CURRENT WORKING DIRECTORY, so whoever
    ran ``--update`` decided where the 913 MB corpus lives — commonly whatever
    directory they happened to be in. Pin one location under the agent home and
    always run from it, so the database is found no matter where the agent's
    cwd points. ``SOCIS_YARGEN_HOME`` overrides for an existing download.
    """
    override = os.environ.get("SOCIS_YARGEN_HOME")
    if override:
        return Path(override).expanduser()
    home = os.environ.get("SOCIS_AGENT_HOME")
    base = Path(home) if home else Path.home() / ".socis-agent"
    return base / "tools" / "yargen"


def _yargen_survey(root: Path) -> dict:
    """What the sample set actually is, so flags follow evidence not guesswork.

    yarGen's own defaults hide two failure modes that look identical to a thin
    result: ``-fs`` skips anything over 10 MB SILENTLY, and super rules need
    more than one sample to mean anything. Both are observable here, so neither
    needs to be a question put to the user — who usually cannot answer it in
    advance either.
    """
    files, largest, biggest_name = 0, 0, ""
    formats: dict[str, int] = {}
    for f in root.rglob("*"):
        try:
            if not f.is_file() or f.is_symlink():
                continue
            size = f.stat().st_size
        except OSError:
            continue
        files += 1
        if size > largest:
            largest, biggest_name = size, f.name
        fmt = _file_format(f)
        formats[fmt] = formats.get(fmt, 0) + 1
    return {"files": files, "largest": largest, "largest_name": biggest_name,
            "largest_mb": largest / (1024 * 1024), "formats": formats}


# yarGen's downloadable corpus is built from WINDOWS goodware. Feed it Mach-O
# or ELF samples and its filtering finds nothing to remove, so platform
# boilerplate survives into the rule: a macOS run produced a rule keyed on
# `__mh_execute_header` and Apple OCSP URLs, which matches every signed binary
# on the machine. The rule compiled, scanned, and hit both samples — it looked
# like success at every step. Only the corpus knew better, and it had no way
# to say so.
_MAGIC = (
    (b"MZ", "pe"),
    (b"\x7fELF", "elf"),
    (b"\xcf\xfa\xed\xfe", "macho"),   # 64-bit LE
    (b"\xce\xfa\xed\xfe", "macho"),   # 32-bit LE
    (b"\xca\xfe\xba\xbe", "macho"),   # universal/fat
    (b"PK\x03\x04", "zip"),
)


def _file_format(path: Path) -> str:
    try:
        with path.open("rb") as fh:
            head = fh.read(4)
    except OSError:
        return "other"
    for magic, name in _MAGIC:
        if head.startswith(magic):
            return name
    return "other"


def _yargen_check() -> bool:
    return shutil.which("yarGen") is not None or shutil.which("yargen") is not None


def _handle_yargen(args: dict, **_kw) -> str:
    samples = args.get("samples_dir") or ""
    if not samples.strip():
        return "❌ `samples_dir` is required."
    p = Path(samples)
    if not p.is_dir():
        return f"❌ Not a directory: {samples}"
    binary = "yarGen" if shutil.which("yarGen") else "yargen"

    # yarGen WRITES THE RULE TO A FILE; stdout is only progress and goodware-DB
    # logging. Without -o it drops `yargen_rules.yar` into the process CWD and
    # we returned the log instead — so the caller saw talk about excluded
    # patterns and no rule, and an unread .yar file accumulated in whatever
    # directory the agent happened to be in. Name the output path, then read it.
    # CWD MATTERS: yarGen resolves its goodware `dbs/` relative to the working
    # directory, NOT to yarGen.py. Running it from the temp output dir would
    # find no database and silently emit UNFILTERED rules — rules that match
    # every Windows binary, with nothing in the output saying so. Run from the
    # directory that owns dbs/, and refuse rather than guess if it is absent.
    db_home = _yargen_db_home()
    if not (db_home / "dbs").is_dir():
        try:
            shown = "~/" + str(db_home.relative_to(Path.home()))
        except ValueError:
            shown = str(db_home)
        return (f"❌ yarGen goodware database not found at {shown}/dbs.\n\n"
                "Without it yarGen filters nothing and every rule it writes "
                "matches every Windows binary. Build it with:\n"
                f"  mkdir -p {shown} && cd {shown} && yarGen --update\n"
                "(~913 MB) — or `bash scripts/install.sh --ensure yargen`.")

    survey = _yargen_survey(p)
    if not survey["files"]:
        return f"❌ No files in {samples} — nothing to analyse."

    # Created only AFTER every early return: an earlier revision made the temp
    # dir first, so the missing-database and empty-directory paths returned
    # without reaching the `finally` and left it behind on every failed call.
    out_dir = tempfile.mkdtemp(prefix="socis-yargen-")
    out_path = Path(out_dir) / "yargen_rules.yar"

    argv = [binary, "-m", str(p.resolve()), "-a", args.get("author") or "SOCIS Agent",
            "-o", str(out_path)]
    notes: list[str] = []

    # -fs is a MAX FILE SIZE IN MB and defaults to 10. Anything larger is
    # dropped without a word — a packed dropper or .NET bundle just never
    # appears in the rule, and the output is indistinguishable from "this
    # family had few good strings". Derive it from the set instead: the tool
    # can see the largest file, so the operator should not have to.
    if survey["largest_mb"] > 9:
        fs = max(10, int(survey["largest_mb"]) + 5)
        argv += ["-fs", str(fs)]
        notes.append(
            f"raised the size limit to {fs} MB — largest sample "
            f"({survey['largest_name']}) is {survey['largest_mb']:.1f} MB and "
            "yarGen's 10 MB default would have skipped it silently"
        )

    # Super rules are strings shared ACROSS samples. With one file there is
    # nothing to share, and yarGen spends the time anyway.
    if survey["files"] == 1:
        argv.append("--nosuper")
        notes.append("single sample — skipped super-rule generation (nothing to compare against)")

    if args.get("opcodes"):
        argv.append("--opcodes")
    if args.get("exclude_good"):
        argv.append("--excludegood")
        notes.append("--excludegood: goodware strings dropped outright, not merely down-scored")
    if args.get("min_score") is not None:
        argv += ["-z", str(int(args["min_score"]))]
    if args.get("max_strings") is not None:
        argv += ["-rc", str(int(args["max_strings"]))]
    if args.get("reference"):
        argv += ["-r", str(args["reference"])]
    try:
        res = _run(argv, cwd=str(db_home), timeout=600)  # extraction is slow
        if res.get("error"):
            return f"❌ {res['error']}"
        if not res.get("ok"):
            detail = res.get("stderr") or res.get("stdout") or f"exit {res.get('exit_code')}"
            return f"❌ Failed:\n{detail}"

        if not out_path.is_file():
            return ("❌ yarGen exited 0 but wrote no rule file. Its log follows — "
                    "the usual cause is a missing goodware database "
                    "(`yarGen.py --update`) or a samples directory it could not "
                    f"read.\n\n{res.get('stdout') or '(no output)'}")

        rule = out_path.read_text(encoding="utf-8", errors="replace").strip()
        if not rule:
            return ("⚠ yarGen produced an EMPTY rule file: every candidate string "
                    "was filtered out as goodware. That is a real result, not an "
                    "error — this sample set shares all its strings with benign "
                    "software.\n\n"
                    f"Analysed {survey['files']} file(s). Next: add more samples of "
                    "the same family, or re-run with opcodes=true — yarGen's own "
                    "guidance is to use opcodes when not enough high-scoring "
                    "strings can be found.")

        # A rule over a large sample set can be long; keep the tail rather than
        # the head, since yarGen puts the super-rules last.
        _MAX = 20000
        truncated = len(rule) > _MAX
        if truncated:
            rule = rule[-_MAX:]

        # Report what was decided FROM the sample set, so the reasoning is
        # visible rather than buried in argv.
        fmts = survey.get("formats") or {}
        fmt_desc = ", ".join(f"{n}× {k}" for k, n in
                             sorted(fmts.items(), key=lambda kv: -kv[1]))
        header = (f"✅ {survey['files']} sample(s), largest "
                  f"{survey['largest_mb']:.1f} MB"
                  + (f" ({fmt_desc})" if fmt_desc else "") + ".")
        if notes:
            header += "\n" + "\n".join(f"   • {n}" for n in notes)

        # yarGen analyses EVERY file it is given. A previously-generated .yar
        # left in the samples directory becomes a "sample" and yields a rule
        # built from rule syntax — observed exactly that way in testing.
        other = fmts.get("other", 0)
        if other and other < survey["files"]:
            header += (
                f"\n   • {other} file(s) are not executables (no PE/ELF/Mach-O "
                "magic). yarGen analysed them anyway — check the samples "
                "directory for notes, reports, or previously-generated .yar "
                "files, and remove them before relying on this rule."
            )

        # Corpus mismatch is the failure that looks most like success: the rule
        # compiles, scans, and hits the samples, while being built entirely
        # from platform boilerplate the Windows corpus never had a chance to
        # filter. Say it BEFORE the rule, not after — this is the one thing
        # that decides whether the output is usable.
        non_pe = sum(n for k, n in fmts.items() if k in ("macho", "elf"))
        if non_pe:
            kinds = " and ".join(k for k in ("macho", "elf") if fmts.get(k))
            header += (
                f"\n\n🚨 CORPUS MISMATCH: {non_pe} of {survey['files']} sample(s) "
                f"are {kinds}, but yarGen's downloaded goodware database is built "
                "from WINDOWS binaries. Platform boilerplate "
                "(`__mh_execute_header`, code-signing URLs, ELF section names) "
                "was NOT filtered and will be in the rule below — it may match "
                "every signed binary on the host.\n"
                "   Before trusting this rule: run `yara_scan` against a "
                "goodware directory (/usr/bin, /Applications). ANY hit there "
                "means the rule is not finished. Matching the samples proves "
                "nothing on its own."
            )

        # A thin rule and an absent one fail the same way to a reader: it looks
        # like the family simply had nothing distinctive. Say which it is, and
        # name the documented remedy rather than leaving the caller to guess.
        thin = rule.count("$") < 3
        advice = ""
        if thin and not args.get("opcodes"):
            advice = ("\n\n⚠ Only a handful of strings survived filtering. That is "
                      "yarGen's documented cue for opcodes=true — it falls back to "
                      "opcode sequences when high-scoring strings are scarce. More "
                      "samples of the same family would help more.")

        return (header + "\n\n"
                + f"```yara\n{rule}\n```"
                + ("\n\n[rule truncated — head omitted]" if truncated else "")
                + advice
                + "\n\n⚠ These are CANDIDATES, not a finished rule. Review every "
                  "string: would the author have to change their code, or just "
                  "recompile? Drop anything a recompile defeats, then test with "
                  "`yara_scan` against both the samples AND known-good binaries.")
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


# ── Suricata ─────────────────────────────────────────────────────────────────

def _suricata_check() -> bool:
    return shutil.which("suricata") is not None


def _handle_suricata_check(args: dict, **_kw) -> str:
    rules = args.get("rules") or ""
    if not rules.strip():
        return "❌ `rules` is required (the Suricata rule text)."
    path = _write_temp(rules, ".rules")
    try:
        res = _run(["suricata", "-T", "-S", path])
        out = _fmt(res, on_success="Rules parse.")
        if res.get("ok"):
            out += ("\n\n⚠ Parsing is not evidence the rule works. A Suricata rule can "
                    "parse perfectly and never fire — wrong buffer, inverted `flow:`, "
                    "or encrypted traffic. Replay it against a PCAP before trusting it.")
        return out
    finally:
        Path(path).unlink(missing_ok=True)


def _handle_suricata_replay(args: dict, **_kw) -> str:
    rules = args.get("rules") or ""
    pcap = args.get("pcap") or ""
    if not rules.strip() or not pcap.strip():
        return "❌ Both `rules` and `pcap` are required."
    if not Path(pcap).is_file():
        return f"❌ PCAP not found: {pcap}"
    rules_path = _write_temp(rules, ".rules")
    try:
        with tempfile.TemporaryDirectory() as outdir:
            res = _run(["suricata", "-r", pcap, "-S", rules_path, "-l", outdir], timeout=300)
            if res.get("error"):
                return f"❌ {res['error']}"
            fast = Path(outdir) / "fast.log"
            alerts = fast.read_text(encoding="utf-8", errors="replace").strip() if fast.is_file() else ""
            if alerts:
                return f"✅ Rule fired:\n\n{alerts[:_MAX_OUTPUT]}"
            return ("⚠ NO ALERTS. The rule did not fire on this PCAP.\n\n"
                    "Check in this order:\n"
                    "1. Did Suricata parse the protocol? Look for http/tls events in eve.json.\n"
                    "   No events means the traffic is on a non-standard port.\n"
                    "2. Is `flow:` inverted? `to_server` never matches a response.\n"
                    "3. Is the content in a different buffer? http.uri excludes the host.\n"
                    "4. Is the traffic TLS? Then no payload content will ever match.")
    finally:
        Path(rules_path).unlink(missing_ok=True)


# ── Registration ─────────────────────────────────────────────────────────────

registry.register(
    name="sigma_check",
    toolset="sigma",
    schema={
        "name": "sigma_check",
        "description": "Validate a Sigma rule with sigma-cli. Returns errors and warnings.",
        "input_schema": {
            "type": "object",
            "properties": {"rule": {"type": "string", "description": "Sigma rule YAML."}},
            "required": ["rule"],
        },
    },
    handler=_handle_sigma_check,
    check_fn=_sigma_check,
    description="Validate Sigma rule syntax and structure.",
    emoji="📋",
)

registry.register(
    name="sigma_list",
    toolset="sigma",
    schema={
        "name": "sigma_list",
        "description": (
            "List what this installation can convert to. sigma-cli ships with NO backends — "
            "each SIEM is a separate package — so check `targets` before attempting a "
            "conversion rather than discovering the gap from a failure. `plugins` shows "
            "everything installable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "what": {
                    "type": "string",
                    "enum": ["targets", "pipelines", "plugins", "formats"],
                    "description": (
                        "targets = installed backends; pipelines = installed field mappings; "
                        "plugins = everything installable; formats = output formats for one backend."
                    ),
                },
                "backend": {
                    "type": "string",
                    "description": (
                        "Required when what=formats. STRONGLY RECOMMENDED when "
                        "what=pipelines — unscoped output omits backend-specific "
                        "pipelines such as splunk_windows."
                    ),
                },
            },
            "required": ["what"],
        },
    },
    handler=_handle_sigma_list,
    check_fn=_sigma_check,
    description="List installed Sigma backends, pipelines and formats.",
    emoji="📚",
)

registry.register(
    name="sigma_convert",
    toolset="sigma",
    schema={
        "name": "sigma_convert",
        "description": (
            "Convert a Sigma rule to one or more SIEM query languages. Always pass "
            "`pipelines` — without them field names stay generic and the query can be "
            "valid yet never match. Check available backends with sigma_list first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rule": {"type": "string", "description": "Sigma rule YAML."},
                "target": {
                    "type": "string",
                    "description": (
                        "Backend identifier, e.g. splunk, esql, elasticsearch, qradar, "
                        "insightidr, loki, microsoft365defender, sentinel_pipeline. Must be "
                        "installed — see sigma_list."
                    ),
                },
                "pipelines": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Field-mapping pipelines, applied in order — e.g. [\"splunk_windows\"] "
                        "for the splunk backend. Pipelines are BACKEND-SCOPED: check with "
                        "sigma_list (what=pipelines, backend=splunk) rather than the unscoped "
                        "list, which shows a different set. A name that is not installed fails "
                        "the conversion; a wrong but installed one produces a query that runs "
                        "and matches nothing."
                    ),
                },
                "format": {
                    "type": "string",
                    "description": (
                        "Output format for backends that offer more than a bare query, e.g. "
                        "savedsearches for Splunk. List them with sigma_list what=formats."
                    ),
                },
            },
            "required": ["rule", "target"],
        },
    },
    handler=_handle_sigma_convert,
    check_fn=_sigma_check,
    description="Convert Sigma to SIEM-specific queries.",
    emoji="🔄",
)

registry.register(
    name="yara_compile",
    toolset="yara",
    schema={
        "name": "yara_compile",
        "description": "Compile a YARA rule to check it is syntactically valid.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rule": {"type": "string", "description": "YARA rule text."},
                "rule_file": {"type": "string", "description": "Path to a .yar file, as an alternative to `rule`."},
            },
        },
    },
    handler=_handle_yara_compile,
    check_fn=_yara_check,
    description="Compile-check a YARA rule.",
    emoji="🧬",
)

registry.register(
    name="yara_scan",
    toolset="yara",
    schema={
        "name": "yara_scan",
        "description": (
            "Scan a path with a YARA rule. Use against a sample set to confirm the rule "
            "matches, and against a goodware corpus to prove it does not false-positive. "
            "Any hit on goodware means the rule is not finished."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rule": {"type": "string", "description": "YARA rule text."},
                "rule_file": {"type": "string", "description": "Path to a .yar file, as an alternative to `rule`. Use this for a rule already on disk — passing its path as `rule` makes YARA parse the path itself."},
                "path": {"type": "string", "description": "File or directory to scan (scanned recursively)."},
            },
            "required": ["path"],
        },
    },
    handler=_handle_yara_scan,
    check_fn=_yara_check,
    description="Scan files with a YARA rule; shows which strings matched.",
    emoji="🔍",
)

registry.register(
    name="yargen_generate",
    toolset="yara",
    schema={
        "name": "yargen_generate",
        "description": (
            "Generate a YARA rule from malware samples with yarGen, filtered against its "
            "goodware database. Returns the rule text. File-size limit and super-rule "
            "handling are DERIVED from the sample set — do not ask the user for them. "
            "Output is a starting point for triage, not a finished rule."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "samples_dir": {"type": "string", "description": "Directory of samples. Several samples of one family beat a single file."},
                "author": {"type": "string", "description": "Author for rule metadata. Defaults to \"SOCIS Agent\"; only set this to credit a human analyst."},
                "opcodes": {"type": "boolean", "description": "Fall back to opcode sequences. yarGen's own guidance: use when not enough high-scoring strings are found. Slower and much more memory."},
                "exclude_good": {"type": "boolean", "description": "Drop goodware strings outright instead of down-scoring them. Fewer false positives, but can empty a rule for a family that reuses common code."},
                "min_score": {"type": "integer", "description": "Score floor for a string (yarGen default 0). Raise only after a first run shows low-value strings surviving — guessing a floor blind can empty the rule."},
                "max_strings": {"type": "integer", "description": "Max strings per rule (yarGen default 20)."},
                "reference": {"type": "string", "description": "Reference for rule metadata — a case id, report URL, or sample source."},
            },
            "required": ["samples_dir"],
        },
    },
    handler=_handle_yargen,
    check_fn=_yargen_check,
    description="Generate candidate YARA strings from samples.",
    emoji="⚗️",
)

registry.register(
    name="suricata_check",
    toolset="suricata",
    schema={
        "name": "suricata_check",
        "description": "Validate Suricata rule syntax. Parsing does not mean the rule fires.",
        "input_schema": {
            "type": "object",
            "properties": {"rules": {"type": "string", "description": "Suricata rule text."}},
            "required": ["rules"],
        },
    },
    handler=_handle_suricata_check,
    check_fn=_suricata_check,
    description="Syntax-check Suricata rules.",
    emoji="🛡️",
)

registry.register(
    name="suricata_replay",
    toolset="suricata",
    schema={
        "name": "suricata_replay",
        "description": (
            "Replay a PCAP against Suricata rules and report alerts. This is the step that "
            "decides whether a rule works — a rule that parses but does not fire is not done."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rules": {"type": "string", "description": "Suricata rule text."},
                "pcap": {"type": "string", "description": "Path to the PCAP file."},
            },
            "required": ["rules", "pcap"],
        },
    },
    handler=_handle_suricata_replay,
    check_fn=_suricata_check,
    description="Replay a PCAP to confirm a rule actually fires.",
    emoji="📡",
)

__all__ = ["_sigma_check", "_yara_check", "_yargen_check", "_suricata_check"]
