"""Regression tests for `yargen_generate` and the YARA rule-input helpers.

Every case here corresponds to a failure that shipped and was diagnosed from a
real session, not to a hypothetical. They share one shape: the tool returned
something that READ like success. A rule that was really a log, a scan of an
empty directory reported as "no false positives", a rule built from platform
boilerplate because the goodware corpus was for a different OS. None of them
raised, so none of them would be caught by a test that only asserts "no
exception".

No yarGen binary and no 913 MB corpus is required: a stub on PATH stands in for
the real one, and the assertions are about the arguments SOCIS chooses and the
text it returns.
"""

import os
import pathlib
import stat
from pathlib import Path

import pytest

from tools.detection_tools import (
    _file_format,
    _fence_for,
    _handle_sigma_check,
    _handle_sigma_convert,
    _handle_suricata_check,
    _handle_suricata_replay,
    _resolve_suricata_rules,
    _handle_yara_scan,
    _handle_yargen,
    _resolve_rule_text,
    _yargen_survey,
)

# Real magic bytes. Written via Path.write_bytes rather than `printf '\xcf...'`,
# which emits literal backslash characters in sh and silently produced "other"
# for every sample the first time these fixtures were built.
PE = b"MZ"
ELF = b"\x7fELF"
MACHO64 = b"\xcf\xfa\xed\xfe"
MACHO_FAT = b"\xca\xfe\xba\xbe"


def _sample(directory: Path, name: str, magic: bytes, size: int = 2048) -> Path:
    path = directory / name
    path.write_bytes(magic + os.urandom(size))
    return path


@pytest.fixture
def db_home(tmp_path, monkeypatch):
    """A goodware database yarGen can find.

    yarGen resolves ``dbs/`` from the CURRENT WORKING DIRECTORY, not from
    beside yarGen.py. The handler therefore pins a directory and runs from it;
    without ``dbs/`` present it must refuse rather than emit an unfiltered rule.
    """
    home = tmp_path / "yghome"
    (home / "dbs").mkdir(parents=True)
    (home / "dbs" / "good-strings.db").write_bytes(b"stub")
    monkeypatch.setenv("SOCIS_YARGEN_HOME", str(home))
    return home


@pytest.fixture
def stub_yargen(tmp_path, monkeypatch):
    """A yarGen that records its argv and writes a rule to ``-o``.

    Mirrors the real one in the way that matters: the rule goes to a FILE and
    stdout carries only progress chatter. Returning stdout instead of reading
    that file was the original bug.
    """
    bindir = tmp_path / "bin"
    bindir.mkdir()
    argv_log = tmp_path / "argv.txt"
    script = bindir / "yarGen"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "argv = sys.argv[1:]\n"
        f"open({str(argv_log)!r}, 'w').write(json.dumps(argv))\n"
        "out = [argv[i + 1] for i, a in enumerate(argv) if a == '-o'][0]\n"
        "n = int(os.environ.get('STUB_STRINGS', '5'))\n"
        "body = '\\n'.join('      $s%d = \"cand_%d\" ascii' % (i, i) for i in range(n))\n"
        "print('Reading goodware strings from database ...')\n"
        "open(out, 'w').write(\n"
        "    'rule fam {\\n   strings:\\n' + body + '\\n   condition:\\n      all of them\\n}\\n'\n"
        "    if n else ''\n"
        ")\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    return argv_log


def _argv(argv_log: Path) -> list:
    import json

    return json.loads(argv_log.read_text())


# ── survey: the evidence the flags are derived from ─────────────────────────


def test_survey_counts_files_and_finds_largest(tmp_path):
    _sample(tmp_path, "small.bin", PE, 100)
    _sample(tmp_path, "big.bin", PE, 50_000)
    survey = _yargen_survey(tmp_path)
    assert survey["files"] == 2
    assert survey["largest_name"] == "big.bin"


@pytest.mark.parametrize(
    "magic,expected",
    [(PE, "pe"), (ELF, "elf"), (MACHO64, "macho"), (MACHO_FAT, "macho")],
)
def test_file_format_reads_magic_bytes(tmp_path, magic, expected):
    assert _file_format(_sample(tmp_path, "s.bin", magic)) == expected


def test_file_format_unknown_is_other(tmp_path):
    (tmp_path / "notes.txt").write_text("plain text")
    assert _file_format(tmp_path / "notes.txt") == "other"


# ── derived flags ───────────────────────────────────────────────────────────


def test_large_sample_raises_the_size_limit(tmp_path, db_home, stub_yargen):
    """yarGen's -fs default is 10 MB and it skips bigger files SILENTLY.

    A packed dropper then never reaches the rule and the output is
    indistinguishable from a family with few good strings.
    """
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "packed.exe", PE, 12 * 1024 * 1024)
    out = _handle_yargen({"samples_dir": str(samples)})
    argv = _argv(stub_yargen)
    assert "-fs" in argv, "no size limit passed for a >10 MB sample"
    assert int(argv[argv.index("-fs") + 1]) > 12
    assert "raised the size limit" in out


def test_small_samples_do_not_set_a_size_limit(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE, 1024)
    _handle_yargen({"samples_dir": str(samples)})
    assert "-fs" not in _argv(stub_yargen)


def test_single_sample_skips_super_rules(tmp_path, db_home, stub_yargen):
    """Super rules are strings shared ACROSS samples; one file shares nothing."""
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "only.exe", PE)
    out = _handle_yargen({"samples_dir": str(samples)})
    assert "--nosuper" in _argv(stub_yargen)
    assert "single sample" in out


def test_multiple_samples_keep_super_rules(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _sample(samples, "b.exe", PE)
    _handle_yargen({"samples_dir": str(samples)})
    assert "--nosuper" not in _argv(stub_yargen)


def test_author_defaults_to_socis_agent(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _handle_yargen({"samples_dir": str(samples)})
    argv = _argv(stub_yargen)
    assert argv[argv.index("-a") + 1] == "SOCIS Agent"


def test_optional_parameters_are_passed_through(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _handle_yargen(
        {
            "samples_dir": str(samples),
            "opcodes": True,
            "exclude_good": True,
            "min_score": 30,
            "max_strings": 40,
            "reference": "CASE-1",
        }
    )
    argv = _argv(stub_yargen)
    assert "--opcodes" in argv and "--excludegood" in argv
    assert argv[argv.index("-z") + 1] == "30"
    assert argv[argv.index("-rc") + 1] == "40"
    assert argv[argv.index("-r") + 1] == "CASE-1"


# ── corpus mismatch: the failure that looked like success ───────────────────


@pytest.mark.parametrize("magic,kind", [(MACHO64, "macho"), (ELF, "elf")])
def test_non_windows_samples_warn_about_the_corpus(
    tmp_path, db_home, stub_yargen, magic, kind
):
    """The downloadable corpus is WINDOWS goodware.

    Fed Mach-O or ELF it filters nothing, so platform boilerplate survives into
    the rule. Observed live: a rule keyed on `__mh_execute_header` and Apple
    OCSP URLs that compiled, scanned, matched its samples — and matched every
    signed binary on the host.
    """
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.bin", magic)
    out = _handle_yargen({"samples_dir": str(samples)})
    assert "CORPUS MISMATCH" in out
    assert kind in out


def test_pe_samples_do_not_warn(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _sample(samples, "b.exe", PE)
    assert "CORPUS MISMATCH" not in _handle_yargen({"samples_dir": str(samples)})


def test_stray_non_executable_is_flagged(tmp_path, db_home, stub_yargen):
    """yarGen analyses every file it is given.

    A rule file left in the samples directory from a previous run becomes a
    "sample" and yields a rule built from rule syntax — observed exactly that
    way.
    """
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _sample(samples, "b.exe", PE)
    (samples / "previous_rules.yar").write_text("rule old { condition: true }")
    out = _handle_yargen({"samples_dir": str(samples)})
    assert "not executables" in out


# ── failure paths must explain themselves ───────────────────────────────────


def test_missing_database_refuses_rather_than_guessing(tmp_path, monkeypatch, stub_yargen):
    """Without dbs/ yarGen filters NOTHING and every rule matches everything."""
    monkeypatch.setenv("SOCIS_YARGEN_HOME", str(tmp_path / "absent"))
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    out = _handle_yargen({"samples_dir": str(samples)})
    assert "goodware database not found" in out
    assert "matches every Windows binary" in out


def test_empty_rule_is_reported_as_a_real_result(
    tmp_path, db_home, stub_yargen, monkeypatch
):
    monkeypatch.setenv("STUB_STRINGS", "0")
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    out = _handle_yargen({"samples_dir": str(samples)})
    assert "EMPTY rule file" in out
    assert "real result" in out


def test_empty_directory_is_rejected(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    assert "No files in" in _handle_yargen({"samples_dir": str(samples)})


def test_no_temp_directories_are_left_behind(tmp_path, monkeypatch, stub_yargen):
    """Early returns once ran AFTER mkdtemp and leaked on every failed call."""
    import tempfile

    monkeypatch.setenv("SOCIS_YARGEN_HOME", str(tmp_path / "absent"))
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    before = set(Path(tempfile.gettempdir()).glob("socis-yargen-*"))
    _handle_yargen({"samples_dir": str(samples)})
    _handle_yargen({"samples_dir": str(tmp_path / "does-not-exist")})
    assert set(Path(tempfile.gettempdir()).glob("socis-yargen-*")) == before


# ── rule input: text, file, or a path passed as text ────────────────────────


def test_rule_text_is_used_directly():
    text, err = _resolve_rule_text({"rule": "rule t { condition: true }"})
    assert not err and text.startswith("rule t")


def test_rule_file_is_read(tmp_path):
    f = tmp_path / "r.yar"
    f.write_text("rule fromfile { condition: true }")
    text, err = _resolve_rule_text({"rule_file": str(f)})
    assert not err and "fromfile" in text


def test_a_path_passed_as_rule_is_resolved(tmp_path):
    """YARA parsed the PATH as rule source and failed with an unattributable
    `syntax error, unexpected regular expression` on a temp file the caller
    never created — which pushed one agent into shelling out to raw yara."""
    f = tmp_path / "r.yar"
    f.write_text("rule fromfile { condition: true }")
    text, err = _resolve_rule_text({"rule": str(f)})
    assert not err and "fromfile" in text


def test_missing_rule_file_is_named(tmp_path):
    _, err = _resolve_rule_text({"rule_file": str(tmp_path / "nope.yar")})
    assert "not found" in err


def test_wrong_key_holding_a_rule_path_is_diagnosed(tmp_path):
    """`path` belongs to yara_scan, not yara_compile. Listing only the valid
    names read as "this tool is broken" and the tool was abandoned."""
    f = tmp_path / "r.yar"
    f.write_text("rule x { condition: true }")
    _, err = _resolve_rule_text({"path": str(f)})
    assert "rule_file" in err and str(f) in err


def test_neither_rule_nor_rule_file():
    _, err = _resolve_rule_text({})
    assert "rule" in err and "rule_file" in err


# ── scanning nothing is not a clean result ──────────────────────────────────


def test_scanning_an_empty_directory_is_not_a_pass(tmp_path, monkeypatch):
    """Observed: an empty goodware directory summarised as "no false
    positives ✅" — the strongest claim this tooling makes, on zero files."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    yara = bindir / "yara"
    yara.write_text("#!/usr/bin/env bash\nexit 0\n")
    yara.chmod(yara.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")

    empty = tmp_path / "goodware"
    empty.mkdir()
    out = _handle_yara_scan({"rule": "rule t { condition: false }", "path": str(empty)})
    assert "NO FILES" in out
    assert "not a clean result" in out

    populated = tmp_path / "corpus"
    populated.mkdir()
    _sample(populated, "a.exe", PE)
    out = _handle_yara_scan(
        {"rule": "rule t { condition: false }", "path": str(populated)}
    )
    assert "No matches" in out and "1 file(s) scanned" in out


# ── Sigma takes the same rule input as YARA ─────────────────────────────────


@pytest.fixture
def stub_sigma(tmp_path, monkeypatch):
    """A sigma-cli that echoes the YAML it was actually given."""
    bindir = tmp_path / "sbin"
    bindir.mkdir()
    script = bindir / "sigma"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "args = [a for a in sys.argv[1:] if not a.startswith('-')]\n"
        "f = [a for a in args if a.endswith(('.yml', '.yaml'))]\n"
        "print('SAW:', open(f[-1]).read().strip()[:80] if f else '(none)')\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    return bindir


@pytest.fixture
def sigma_rule(tmp_path):
    f = tmp_path / "rule.yml"
    f.write_text("title: Suspicious PowerShell\ndetection:\n  condition: sel\n")
    return f


def test_sigma_check_accepts_rule_file(stub_sigma, sigma_rule):
    assert "Suspicious PowerShell" in _handle_sigma_check({"rule_file": str(sigma_rule)})


def test_sigma_check_resolves_a_path_passed_as_rule(stub_sigma, sigma_rule):
    """sigma would otherwise parse the PATH as YAML."""
    assert "Suspicious PowerShell" in _handle_sigma_check({"rule": str(sigma_rule)})


def test_sigma_check_still_accepts_yaml_text(stub_sigma):
    assert "title: X" in _handle_sigma_check({"rule": "title: X"})


def test_sigma_convert_accepts_rule_file(stub_sigma, sigma_rule):
    out = _handle_sigma_convert({"rule_file": str(sigma_rule), "target": "splunk"})
    assert "Suspicious PowerShell" in out


def test_sigma_convert_without_a_rule_names_both_options(stub_sigma):
    err = _handle_sigma_convert({"target": "splunk"})
    assert "rule_file" in err


def test_sigma_convert_without_a_target_says_so(stub_sigma, sigma_rule):
    err = _handle_sigma_convert({"rule_file": str(sigma_rule)})
    assert "`target` is required" in err


def test_sigma_convert_warns_when_no_pipeline_is_set(stub_sigma, sigma_rule):
    """A pipeline-less query can be valid and still never match anything —
    the most expensive kind of wrong, because it looks like a detection."""
    out = _handle_sigma_convert({"rule_file": str(sigma_rule), "target": "splunk"})
    assert "No pipeline specified" in out


def test_sigma_convert_passes_pipelines_in_order(stub_sigma, sigma_rule, tmp_path):
    log = tmp_path / "argv.txt"
    script = stub_sigma / "sigma"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"open({str(log)!r}, 'w').write(json.dumps(sys.argv[1:]))\n"
        "print('ok')\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    _handle_sigma_convert({
        "rule_file": str(sigma_rule), "target": "splunk",
        "pipelines": ["splunk_windows", "splunk_cim"],
    })
    import json
    argv = json.loads(log.read_text())
    assert argv.count("-p") == 2
    assert argv.index("splunk_windows") < argv.index("splunk_cim")


def test_sigma_convert_accepts_a_single_pipeline_as_a_string(
    stub_sigma, sigma_rule, tmp_path
):
    """The schema must permit what the handler coerces.

    Validation runs before the handler, so a strict `array` type rejected
    `pipelines: "splunk_windows"` outright and the handler's string coercion
    could never run — a wasted round trip on the commonest case.
    """
    log = tmp_path / "argv.txt"
    script = stub_sigma / "sigma"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"open({str(log)!r}, 'w').write(json.dumps(sys.argv[1:]))\n"
        "print('ok')\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    _handle_sigma_convert({
        "rule_file": str(sigma_rule), "target": "splunk",
        "pipelines": "splunk_windows",
    })
    import json
    argv = json.loads(log.read_text())
    assert argv.count("-p") == 1
    assert "splunk_windows" in argv


def test_sigma_convert_schema_permits_string_or_array():
    """Guard the schema itself, not just the handler."""
    import ast as _ast
    import re as _re
    src = pathlib.Path("tools/detection_tools.py").read_text(encoding="utf-8")
    m = _re.search(
        r'registry\.register\(\s*name="sigma_convert".*?schema=(\{.*?\}),\s*\n\s*handler=',
        src, _re.S,
    )
    schema = _ast.literal_eval(m.group(1))
    pl = schema["input_schema"]["properties"]["pipelines"]["type"]
    assert "string" in pl and "array" in pl, f"pipelines type is {pl!r}"


# ── Output is Markdown, and the reference names provenance ─────────────────


def test_converted_query_is_fenced_with_the_backend_language(stub_sigma, sigma_rule):
    """A SIEM query is pasted into a search bar verbatim.

    Unfenced, the desktop chat reflows it as prose and a collapsed line break
    or lost indentation is not cosmetic.
    """
    script = stub_sigma / "sigma"
    script.write_text(
        "#!/usr/bin/env python3\nprint('Image=\"*powershell.exe\"')\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    out = _handle_sigma_convert({
        "rule_file": str(sigma_rule), "target": "splunk",
        "pipelines": ["splunk_windows"],
    })
    assert "```spl" in out and out.rstrip().endswith("```")
    assert "splunk_windows" in out


@pytest.mark.parametrize(
    "target,expected",
    [("splunk", "spl"), ("kusto", "kql"), ("loki", "logql"),
     ("eql", "eql"), ("elastalert", "yaml"), ("no_such_backend", "text")],
)
def test_fence_language_per_backend(target, expected):
    assert _fence_for(target) == expected


@pytest.mark.parametrize(
    "fmt,expected",
    [
        # Sigma's splunk backend offers default / savedsearches / data_model.
        # Matching only the substring "conf" caught one of the three, so
        # `savedsearches` — which emits .conf stanzas — was fenced as spl.
        ("savedsearches", "ini"),
        ("savedsearches.conf", "ini"),
        ("data_model", "json"),
        ("default", "spl"),
        ("", "spl"),
        ("yaml", "yaml"),
        ("json", "json"),
    ],
)
def test_output_format_overrides_the_backend_language(fmt, expected):
    """Non-default formats emit config files, not a bare query."""
    assert _fence_for("splunk", fmt) == expected


def test_yargen_reference_defaults_to_the_socis_rules_repo(
    tmp_path, db_home, stub_yargen
):
    """yarGen stamps its OWN repo when -r is absent, so every rule pointed at
    the generator instead of its provenance."""
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _handle_yargen({"samples_dir": str(samples)})
    argv = _argv(stub_yargen)
    ref = argv[argv.index("-r") + 1]
    assert "socisio/socis-rules" in ref
    assert "Neo23x0" not in ref


def test_explicit_reference_wins(tmp_path, db_home, stub_yargen):
    samples = tmp_path / "samples"
    samples.mkdir()
    _sample(samples, "a.exe", PE)
    _handle_yargen({"samples_dir": str(samples), "reference": "CASE-4471"})
    argv = _argv(stub_yargen)
    assert argv[argv.index("-r") + 1] == "CASE-4471"


def test_sigma_convert_description_rules_out_a_yara_target():
    """The description is in context whenever the tool is loaded.

    Asked "can I convert Sigma to YARA?", the agent answered "yes, with
    caveats" and offered to do it with sigma_convert — describing a capability
    that does not exist. The skill covering this was never loaded, because a
    conversational question does not trigger skill loading. The tool
    description is the one place the fact is always present.
    """
    import ast as _ast
    import re as _re
    src = pathlib.Path("tools/detection_tools.py").read_text(encoding="utf-8")
    m = _re.search(
        r'registry\.register\(\s*name="sigma_convert".*?schema=(\{.*?\}),\s*\n\s*handler=',
        src, _re.S,
    )
    desc = _ast.literal_eval(m.group(1))["description"].lower()
    assert "no yara target" in desc
    assert "log events" in desc and "file contents" in desc


# ── Suricata: the same rule-input gap, plus the multi-line trap ─────────────


@pytest.fixture
def stub_suricata(tmp_path, monkeypatch):
    bindir = tmp_path / "surbin"
    bindir.mkdir()
    script = bindir / "suricata"
    script.write_text("#!/usr/bin/env bash\nexit 0\n")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{bindir}{os.pathsep}{os.environ['PATH']}")
    return bindir


@pytest.fixture
def rules_file(tmp_path):
    f = tmp_path / "onion.rules"
    f.write_text('alert udp any any -> any 53 (msg:"onion"; sid:2100001; rev:1;)\n')
    return f


def test_suricata_check_accepts_a_rules_file(stub_suricata, rules_file):
    assert "parse" in _handle_suricata_check({"rules_file": str(rules_file)})


def test_suricata_check_resolves_a_path_passed_as_rules(stub_suricata, rules_file):
    assert "parse" in _handle_suricata_check({"rules": str(rules_file)})


def test_a_multiline_rule_is_diagnosed_not_passed_through():
    """Suricata needs one line per rule, or trailing backslashes.

    A readable multi-line rule fails with `Signature missing required value
    "sid"` even when the sid is right there, because the parser stopped at the
    first newline. An agent spent three turns concluding the TOOL was mangling
    its input.
    """
    multiline = (
        'alert udp $HOME_NET any -> $EXTERNAL_NET 53 (\n'
        '    msg:"onion dns";\n'
        '    sid:2100001; rev:1;\n'
        ')'
    )
    _, err = _resolve_suricata_rules({"rules": multiline})
    assert "multiple lines without continuations" in err
    assert "sid" in err, "must name the misleading error it would have produced"


def test_backslash_continuations_are_accepted():
    ok = (
        'alert udp any any -> any 53 ( \\\n'
        '    msg:"onion dns"; \\\n'
        '    sid:2100001; rev:1;)'
    )
    text, err = _resolve_suricata_rules({"rules": ok})
    assert not err, err
    assert "sid:2100001" in text


def test_a_single_line_rule_is_accepted():
    text, err = _resolve_suricata_rules(
        {"rules": 'alert udp any any -> any 53 (msg:"x"; sid:1; rev:1;)'})
    assert not err and "sid:1" in text


def test_comments_do_not_trigger_the_multiline_check():
    text, err = _resolve_suricata_rules({"rules": (
        '# detects onion dns\n'
        'alert udp any any -> any 53 (msg:"x"; sid:1; rev:1;)\n')})
    assert not err, err


def test_suricata_missing_rules_names_both_options():
    _, err = _resolve_suricata_rules({"pcap": "/tmp/x.pcap"})
    assert "rules_file" in err and "pcap" in err


# ── a null replay must not be reported as a broken rule ────────────────────


def _stub_suricata_replay(bindir, mode):
    """A suricata that writes eve.json with a chosen set of event types."""
    script = bindir / "suricata"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, json, os\n"
        "a = sys.argv[1:]\n"
        "o = a[a.index('-l') + 1] if '-l' in a else '.'\n"
        "os.makedirs(o, exist_ok=True)\n"
        f"mode = {mode!r}\n"
        "if mode == 'alert':\n"
        "    open(os.path.join(o, 'fast.log'), 'w').write('[1:1:1] fired\\n')\n"
        "evs = [{'event_type': 'flow'}] * 4 + [{'event_type': 'stats'}]\n"
        "if mode == 'dns_present':\n"
        "    evs += [{'event_type': 'dns'}] * 3\n"
        "with open(os.path.join(o, 'eve.json'), 'w') as f:\n"
        "    [f.write(json.dumps(e) + '\\n') for e in evs]\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)


def test_null_replay_reports_what_the_capture_contained(stub_suricata, tmp_path):
    """Zero alerts has two OPPOSITE causes.

    A .onion DNS rule replayed against a capture holding only TCP-to-SOCKS
    traffic produces zero alerts while being UNTESTED, not broken. The old
    message said only "the rule did not fire" and went straight to a debugging
    checklist — which discards a working rule. The skill said the same thing:
    "No alert means the rule does not work, whatever it looks like."
    """
    _stub_suricata_replay(stub_suricata, "no_dns")
    pcap = tmp_path / "t.pcap"
    pcap.write_bytes(b"fake")
    out = _handle_suricata_replay({
        "rules": 'alert dns any any -> any any (msg:"x"; dns_query; content:".onion"; sid:1; rev:1;)',
        "pcap": str(pcap)})
    assert "CANNOT TEST this rule" in out, "must resolve the branch, not restate both"
    assert "flow (4)" in out, "must list the event types actually parsed"
    assert "UNTESTED, not broken" in out
    assert "dns" not in out.split("Event types parsed:")[1].split("\n")[0]


def test_null_replay_lists_dns_when_it_was_present(stub_suricata, tmp_path):
    """With the protocol present, a null result DOES mean the rule is wrong."""
    _stub_suricata_replay(stub_suricata, "dns_present")
    pcap = tmp_path / "t.pcap"
    pcap.write_bytes(b"fake")
    out = _handle_suricata_replay({"rules": 'alert dns any any -> any any (msg:"x"; sid:1; rev:1;)',
                                   "pcap": str(pcap)})
    assert "dns (3)" in out
    assert "the rule is wrong" in out


def test_replay_reports_alerts_when_the_rule_fires(stub_suricata, tmp_path):
    _stub_suricata_replay(stub_suricata, "alert")
    pcap = tmp_path / "t.pcap"
    pcap.write_bytes(b"fake")
    out = _handle_suricata_replay({"rules": 'alert tcp any any -> any 9150 (msg:"x"; sid:1; rev:1;)',
                                   "pcap": str(pcap)})
    assert out.startswith("✅") and "fired" in out


def test_replay_accepts_a_rules_file(stub_suricata, tmp_path, rules_file):
    _stub_suricata_replay(stub_suricata, "alert")
    pcap = tmp_path / "t.pcap"
    pcap.write_bytes(b"fake")
    out = _handle_suricata_replay({"rules_file": str(rules_file), "pcap": str(pcap)})
    assert out.startswith("✅")


def test_replay_missing_pcap_is_named(stub_suricata, rules_file):
    out = _handle_suricata_replay({"rules_file": str(rules_file),
                                   "pcap": "/tmp/definitely-not-here.pcap"})
    assert "PCAP not found" in out


@pytest.mark.parametrize("rules_key,pcap_key", [
    ("rules_file", "pcap"),
    ("rules_path", "pcap_path"),
    ("rule_file", "pcap_file"),
    ("rule_path", "pcap"),
])
def test_replay_accepts_path_shaped_aliases(
    stub_suricata, tmp_path, rules_file, rules_key, pcap_key
):
    """`pcap_path` / `rules_path` was the sixth parameter-name miss of the day
    across these tools. A name should not cost a round trip."""
    _stub_suricata_replay(stub_suricata, "alert")
    pcap = tmp_path / "t.pcap"
    pcap.write_bytes(b"fake")
    out = _handle_suricata_replay({rules_key: str(rules_file), pcap_key: str(pcap)})
    assert out.startswith("✅"), f"{rules_key}+{pcap_key} was rejected"
