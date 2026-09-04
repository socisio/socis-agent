---
title: "Performing Fuzzing With Aflplusplus — Performs coverage-guided fuzzing of compiled binaries with"
sidebar_label: "Performing Fuzzing With Aflplusplus"
description: "Performs coverage-guided fuzzing of compiled binaries with"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Performing Fuzzing With Aflplusplus

Performs coverage-guided fuzzing of compiled binaries with

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/performing-fuzzing-with-aflplusplus` |
| Path | `optional-skills/security/performing-fuzzing-with-aflplusplus` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `fuzzing`, `aflplusplus`, `coverage-guided`, `crash-triage`, `binary-analysis`, `security-testing` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Performing Fuzzing with AFL++

## Overview

AFL++ is a community-maintained fork of American Fuzzy Lop (AFL) that provides coverage-guided
fuzzing for compiled binaries. It instruments targets at compile time or via QEMU/Unicorn mode
for binary-only fuzzing, then mutates input corpora to discover new code paths. AFL++ includes
advanced scheduling (MOpt, rare), custom mutators, CMPLOG for input-to-state comparison solving,
and persistent mode for high-throughput fuzzing.


## When to Use

- When conducting security assessments that involve performing fuzzing with aflplusplus
- When following incident response procedures for related security events
- When performing scheduled security testing or auditing activities
- When validating security controls through hands-on testing

## Prerequisites

- AFL++ installed (`apt install afl++` or build from source)
- Target binary source code (for compile-time instrumentation) or QEMU mode for binary-only
- Initial seed corpus of valid inputs for the target format
- Linux system with /proc/sys/kernel/core_pattern configured

## Steps

1. Instrument the target binary with `afl-cc` or `afl-clang-fast`
2. Prepare seed corpus directory with minimal valid inputs
3. Minimize corpus with `afl-cmin` to remove redundant seeds
4. Run `afl-fuzz` with appropriate flags (-i input -o output)
5. Monitor fuzzing progress via afl-whatsup and UI stats
6. Triage crashes with `afl-tmin` minimization and CASR/GDB analysis
7. Report unique crashes with reproduction steps

## Expected Output

```
+++ Findings +++
  unique crashes: 12
  unique hangs: 3
  last crash: 00:02:15 ago
+++ Coverage +++
  map density: 4.23% / 8.41%
  paths found: 1847
  exec speed: 2145/sec
```
