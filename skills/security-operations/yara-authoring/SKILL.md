---
name: yara-authoring
description: "Write YARA rules that survive contact with real data."
version: 1.0.0
author: SOCIS
license: MIT
platforms: [linux, macos, windows]
category: security-operations
triggers:
  - "write a yara rule"
  - "generate yara from this sample"
  - "detect this malware family"
  - "yara rule for this hash"
  - "why is my yara rule matching everything"
toolsets:
  - terminal
  - file
  - yara
metadata:
  socis:
    tags: [Security, DetectionEngineering, YARA, MalwareAnalysis]
    related_skills: [detection-engineering, ioc-enrichment, attack-mapping]
---

# YARA Rule Authoring

A YARA rule is easy to write and hard to write *well*. The failure modes are
asymmetric: a rule that misses costs you one detection, a rule that
false-positives on a system DLL costs you an analyst's afternoon and, after the
third time, their trust in the whole ruleset.

This skill is about the second problem.

---

## Guardrails

1. **Never run an unknown sample.** Rule authoring is static analysis. If
   dynamic behaviour is needed, that is a sandbox task with its own isolation,
   not something to do on an analyst workstation.
2. **Never upload customer samples to a public service.** Hashes are fine.
   Files are not — submitting to VirusTotal or a public sandbox publishes them,
   and paying subscribers can retrieve them. This has leaked real customer data
   for other organisations.
3. **A rule that has not been tested against goodware is not finished.** It is
   a draft. See step 5 — this is the step people skip and the reason rulesets
   get disabled.
4. **Never match on the sample's hash alone.** That is an IOC, not a rule.
   YARA earns its cost by catching the *next* variant.
5. **Present every rule inside a ```yara fenced code block** — pass the
   tool's own fence through rather than retyping the rule as prose. A rule is
   copied verbatim into a file; reflowed as prose it loses line breaks and
   indentation, and a string like `"\\cscript.exe "` silently loses a
   backslash or a trailing space that the match depends on.
   `yargen_generate` already returns fenced output; keep it.

---

## Prerequisites

```bash
bash ~/.socis-agent/socis-agent/scripts/install.sh --ensure yara
yara --version
```

That is all you need. String extraction and goodware filtering are **built in**
— the `yara` toolset provides them with no external tool:

| Tool | Does |
|---|---|
| `yara_goodware_index` | Builds a goodware string index from paths you choose |
| `yara_extract` | Extracts and scores candidate strings from a sample |
| `yara_compile` / `yara_scan` | Compile-check a rule; scan with it (needs the `yara` binary) |

Build the index once before extracting anything, or nothing gets filtered:

```
index /usr/bin as goodware for YARA rule generation
```

Roughly 90k–160k strings in a few seconds. Index a gold image or application
share from the environment you defend as well — a string common across your
estate is goodware *for you* whether or not it appears in a public corpus.

### On yarGen

`yarGen` (Florian Roth) is the reference implementation of this idea and the
built-in tools follow its approach. **You do not need to install it**, and by
default it is not: it requires a 913 MB goodware database, holds 3 GB resident
(6 GB with `--opcodes`), and is unmaintained — upstream now points at
`yarGen-Go`.

Install it only for **large sample sets**. It loads its corpus once and
amortises that across many files, and it does opcode analysis and "super
rules" from strings shared across a malware family — neither of which the
built-in single-sample path covers. For "what is in this file", the built-in
tools are faster and filter against a more relevant corpus.

If you do install it, the database is required rather than optional:

```bash
bash scripts/install.sh --ensure yargen     # clones, wires PATH, fetches the db
```

Without the database its filtering does nothing and you get a rule full of
`KERNEL32.dll`. **Do not install it by hand unless you know where the corpus
lands**: yarGen writes `dbs/` into the CURRENT WORKING DIRECTORY, not beside
`yarGen.py`, so running `--update` from a repo checkout drops 913 MB there and
`yargen_generate` will not find it. SOCIS pins the location to
`~/.socis-agent/tools/yargen/` and always runs from it;
`SOCIS_YARGEN_HOME` overrides for an existing download. `socis doctor`
reports the binary and the database separately — an installed yarGen with no
database is the dangerous state, because it still emits rules.

### Flags: what to pass, and what not to

`yargen_generate` DERIVES the two flags that matter most from the sample set,
so do not ask for them:

- **`-fs` (max file size, default 10 MB)** — anything larger is skipped
  *silently*. The tool raises it to fit the largest sample; without that a
  packed dropper simply never appears in the rule and the output looks like a
  family with few good strings.
- **`--nosuper`** — super rules compare strings ACROSS samples, so they are
  meaningless for a single file.

Set the rest only with a reason:

| parameter | when |
|---|---|
| `opcodes` | after a run comes back thin — yarGen's own cue for scarce high-scoring strings. Costs ~6 GB resident |
| `exclude_good` | false positives matter more than coverage; can empty a rule for a family reusing common code |
| `min_score` | only after a first run shows low-value strings surviving. Guessing blind empties the rule |
| `max_strings` | default 20 is usually right |
| `reference` | case id, report URL, or sample source, for rule metadata | Also worth having: `yaraQA` lints rules for quality problems,
and `YaraML` (Sophos, Apache-2.0) takes an ML approach from labelled sets.

---

## Procedure

### 1. Understand the sample before extracting anything

```bash
file sample.bin
sha256sum sample.bin
```

Packed or obfuscated? Then the strings you extract are the *packer's*, and
your rule will match every sample using that packer — a spectacular false
positive source. Unpack first, or write the rule against the packer
deliberately and say so in the metadata.

### 2. Extract candidates

Built-in, one sample:

```
extract candidate YARA strings from ./samples/mal.bin with min_score 10
```

`yara_extract` pulls ASCII and UTF-16LE strings, checks each against the
goodware index, and scores what survives. Raise `min_score` to see only likely
keepers; drop it to 0 to see everything with its score and reason.

For a **sample set** where yarGen is installed:

```bash
yarGen -m ./samples --opcodes -a "SOCIS" -o candidates.yar
```

Multiple samples of one family beat a single file either way. yarGen adds
"super rules" built from strings common to the set, which is what makes a rule
generic rather than a fingerprint of one binary — that part has no built-in
equivalent, and it is the main reason to install it.

### 3. Triage the strings — this is the part that needs judgement

The tool scores; it does not decide. Read every string it kept and ask what
makes it durable:

| Keep | Why |
|---|---|
| C2 domains, URI paths, user-agents | attacker infrastructure and habits change slowly |
| Unusual mutex, pipe, registry, service names | often hardcoded and reused across builds |
| Distinctive error or debug strings | rarely edited once written |
| Custom encoding tables, key material | expensive for the author to change |

| Drop | Why |
|---|---|
| Compiler and runtime artefacts | present in thousands of benign binaries |
| Common API and DLL names | `CreateRemoteThread` is not a detection |
| Generic English words and paths | `error`, `C:\\Windows\\Temp` |
| Version stamps, timestamps, build paths | change every build |
| Anything from the packer, if packed | see step 1 |

**The test: would the author have to change their code, or just recompile?**
If a recompile defeats the string, it does not belong in the rule.

### 4. Write the condition

The condition is where a rule becomes generic or brittle.

```yara
rule FamilyName_Component {
    meta:
        author      = "SOCIS"
        date        = "2026-09-06"
        description = "What this detects, in one line"
        reference   = "internal case ID or public report"
        hash        = "sha256 of a sample this was built from"
        tlp         = "AMBER"           // who may see this rule
    strings:
        $s1 = "distinctive-c2-path" ascii
        $s2 = "unusual-mutex-name" wide
        $s3 = { 48 8B ?? ?? 48 89 ?? ?? E8 }   // wildcards survive recompiles
    condition:
        uint16(0) == 0x5A4D and          // PE only — cheap, cuts scan cost hard
        filesize < 2MB and               // bound it
        2 of ($s*)                       // N-of rather than all-of
}
```

Four things that matter:

- **Anchor the file type.** `uint16(0) == 0x5A4D` rejects non-PE files before
  any string matching. On a large scan this is the difference between minutes
  and hours.
- **Bound the filesize.** Prevents the rule scanning a 4GB disk image.
- **Prefer `N of ($s*)` to `all of them`.** All-of breaks when the author
  changes one string. N-of degrades gracefully.
- **Wildcard your byte patterns.** Exact opcode sequences break on recompile;
  `??` on the operands keeps the structure and drops the addresses.

### 5. Test — the step that decides whether the rule is usable

```bash
# compiles?
yarac rule.yar rule.yac

# catches what it should
yara -r rule.yar ./samples/

# quality lint
yaraQA -f rule.yar

# THE IMPORTANT ONE: does it fire on clean systems?
yara -r rule.yar /usr/bin /usr/lib
yara -r rule.yar "C:\\Windows\\System32"
```

**Any hit on goodware means the rule is not finished.** Go back to step 3 and
find the string that did it — `-s` prints which one matched.

Then test against a broader benign corpus if you have one. A rule that is
clean on one machine and noisy across a fleet has simply not met enough
software yet.

### 6. Document and deploy

Deploy to a subset first and watch the hit rate for a few days. A rule firing
hundreds of times a day is a false positive whatever its author intended.

---

## Common failure modes

**The rule matches every file in the directory.** A string survived that is in
the compiler runtime, or the sample was packed and you extracted the packer.

**It matched in testing, then never fires in production.** Usually the
condition is `all of them` and the family rotates one string per build. Loosen
to `N of`.

**It fires on the analyst's own tooling.** Debuggers, packers and offensive
tools share strings with malware. Test against your own toolkit, not just the
OS.

**It catches the sample and nothing else, ever.** The rule is a hash with extra
steps. Get more samples of the family and rebuild from what they share.

**Scans take hours.** No file-type anchor and no filesize bound. Add both
before blaming the engine.

---

## Verification

- [ ] Sample understood — packed or not established before extraction
- [ ] Built from multiple samples where available, not one
- [ ] Every string justified: would it survive a recompile?
- [ ] No compiler, runtime or generic-API strings retained
- [ ] File-type anchor and filesize bound present
- [ ] `N of` used rather than `all of them` unless there is a reason
- [ ] Byte patterns wildcarded on operands
- [ ] Compiles with `yarac`
- [ ] Matches every intended sample
- [ ] **Zero hits across a goodware corpus**
- [ ] `yaraQA` clean, or deviations understood
- [ ] Metadata complete: author, date, description, reference, hash, TLP
- [ ] Nothing customer-identifying submitted to any public service
