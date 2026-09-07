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

---

## Prerequisites

```bash
socis install --ensure yara     # installs the yara engine
yara --version
yarGen -h                       # see below — not installed automatically
```

`yara` is installed by `--ensure yara`. **yarGen is not**, deliberately: it is
useless without a multi-gigabyte goodware database, and a rule generated
without one matches every Windows binary on the system. Both steps are yours
to run:

```bash
git clone https://github.com/Neo23x0/yarGen.git
cd yarGen && pip install -r requirements.txt
python yarGen.py --update       # downloads the goodware databases
```

`yarGen` (Florian Roth) extracts candidate strings from samples and scores them
against a large goodware corpus, which removes the strings that appear in every
Windows binary. There is also `yarGen-Go`, a Go rewrite with a REST API, and
`yaraQA`, which lints rules for quality problems. `YaraML` (Sophos, Apache-2.0)
takes an ML approach from labelled malicious/benign sets.

Install the goodware databases before first use — without them, yarGen's
filtering does nothing and you get a rule full of `KERNEL32.dll`.

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

```bash
yarGen -m ./samples --opcodes -a "SOCIS" -o candidates.yar
```

Multiple samples of the same family beat one. yarGen generates "super rules"
from the strings common to a set, which is what makes a rule generic rather
than a fingerprint of one file.

### 3. Triage the strings — this is the part that needs judgement

yarGen scores; it does not decide. Read every string it kept and ask what
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
