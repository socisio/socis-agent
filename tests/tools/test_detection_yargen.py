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
    _handle_sigma_check,
    _handle_sigma_convert,
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
