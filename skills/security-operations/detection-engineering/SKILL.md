---
name: detection-engineering
description: "Author, convert and tune Sigma rules for any SIEM."
version: 1.0.0
author: SOCIS
license: MIT
platforms: [linux, macos, windows]
category: security-operations
triggers:
  - "write a detection rule"
  - "write a sigma rule"
  - "convert this rule to"
  - "tune this detection"
  - "reduce false positives"
  - "detection as code"
  - "detection coverage"
toolsets:
  - terminal
  - file
  - web
metadata:
  socis:
    tags: [Security, DetectionEngineering, Sigma, SIEM]
    related_skills: [attack-mapping, alert-triage]
---

# Detection Engineering

Write detection logic **once** in Sigma, convert it to whatever the customer
runs. This is what makes a detection library portable across a multi-tenant
estate instead of rewriting every rule per platform.

Sigma is vendor-neutral YAML. `sigma-cli` compiles it to Splunk SPL, Sentinel
and Defender KQL, Elastic (Lucene/EQL/ES|QL), QRadar AQL, Chronicle YARA-L,
OpenSearch, Carbon Black, SentinelOne and others via the pySigma plugin
architecture.

---

## Guardrails

1. **A converted rule is not a tested rule.** Conversion checks syntax, not
   semantics. See "The conversion trap" below — this is the single most common
   way detection work goes wrong.
2. **Never deploy straight to production.** Every rule runs against historical
   data first to measure its real false-positive rate.
3. **A detection with no documented FP profile is not finished.** The analyst
   receiving the alert at 3am needs to know what benign activity looks like.
4. **Do not write rules against fields you have not confirmed exist** in the
   customer's actual schema.

---

## Setup

```bash
pipx install sigma-cli          # or: pip install sigma-cli
sigma plugin list               # see available backends
sigma plugin install splunk
sigma plugin install microsoft365defender
sigma plugin install elasticsearch
```

Backend maturity is uneven. Splunk, Elasticsearch and Sentinel are the most
actively maintained; others may lag the spec or miss modifiers.

---

## Rule anatomy

```yaml
title: Suspicious PsExec-Style Service Creation
id: 8f3e2a1b-4c5d-6e7f-8a9b-0c1d2e3f4a5b   # stable UUID, never reuse
status: experimental                        # experimental → test → stable
description: Detects service creation matching PsExec lateral movement patterns
references:
  - https://attack.mitre.org/techniques/T1569/002/
author: SOCIS
date: 2026-09-04
tags:
  - attack.lateral-movement
  - attack.t1569.002
logsource:
  product: windows
  service: system
detection:
  selection:
    EventID: 7045
    ServiceFileName|contains:
      - '\\PSEXESVC'
      - '-s cmd'
  filter_legitimate:
    ServiceName|startswith: 'ApprovedMgmtAgent_'
  condition: selection and not filter_legitimate
falsepositives:
  - Sanctioned remote administration tooling deployed via PsExec
  - Software distribution systems that install services remotely
level: high
```

**Field discipline that matters:**

- `id` — a real UUID, stable forever. It is how you correlate the same
  detection across every platform and every customer.
- `status` — be honest. `experimental` tells downstream consumers not to page
  anyone on it yet.
- `falsepositives` — write these from real observations, not imagination.
- `level` — drives routing. Inflating severity trains analysts to ignore you.

---

## The conversion trap

**This is the part that bites people.** A Sigma rule can be perfectly valid
YAML, convert without error, and still be silently broken on the target
platform. Causes:

- **Field mapping drift** — Sigma's generic `CommandLine` may be
  `process.command_line`, `ProcessCommandLine`, or a custom onboarded name.
- **Unsupported modifiers** — not every backend implements every Sigma modifier
  (`|re`, `|base64offset`, `|cidr`). Some silently drop them.
- **Case sensitivity** — Sigma is case-insensitive by default; several
  backends are not.
- **Query cost** — a valid conversion can generate a query so expensive the
  SIEM times out or the scheduled search never completes.

So every conversion requires an evidence gate before deployment:

| Check | Record |
|---|---|
| Backend + converter version | `sigma plugin list`, pinned version |
| Exact conversion command | including the `-p` pipeline used |
| Field mapping verified | each Sigma field → actual schema field |
| Modifier handling | any dropped/unsupported modifier |
| Logic parity | converted query means the same thing |
| Known-positive test | a sample that *must* match, does |
| Known-negative test | a benign sample that must *not* match, doesn't |
| Query runtime | within the platform's scheduled-search budget |

Skipping the known-positive test is how teams end up with a detection library
that looks comprehensive and catches nothing.

---

## Conversion

```bash
# Validate first — always
sigma check rules/

# Convert with the pipeline that matches the customer's onboarding
sigma convert -t splunk    -p splunk_windows          rules/psexec.yml
sigma convert -t microsoft365defender                 rules/psexec.yml
sigma convert -t elasticsearch -p ecs_windows         rules/psexec.yml
sigma convert -t qradar_aql -p qradar_fields          rules/psexec.yml

# Deployable artifact rather than a bare query
sigma convert -t splunk -p splunk_windows -f savedsearches rules/psexec.yml
```

The `-p` pipeline is not optional in practice. Without it you get Sigma's
generic field names, which match almost no real deployment.

When a customer's schema is bespoke, write a **custom pipeline** rather than
editing rules per customer — that keeps one rule serving every tenant.

---

## Tuning workflow

Detections decay. Environments change, software gets deployed, the rule that
was clean in March is noisy in June.

1. **Measure before tuning.** Get the actual FP rate over ≥30 days. Do not tune
   on a single complaint.
2. **Prefer narrowing the selection over adding filters.** A tighter
   `selection` is more durable than a growing list of exclusions.
3. **Never filter on attacker-controllable values.** Excluding by process name,
   file path, or command-line string is trivially bypassed. Filter on things
   the attacker cannot set: signing certificate, parent process lineage,
   management-agent identity, asset group.
4. **Record every filter's rationale** in the rule. An unexplained exclusion is
   indistinguishable from a backdoor during audit.
5. **Re-run the known-positive test after every tune.** Tuning that quietly
   kills true-positive coverage is the failure mode here.

---

## Detection-as-code

Treat rules as versioned software:

```
detections/
├── rules/
│   ├── initial-access/
│   ├── execution/
│   ├── persistence/
│   ├── lateral-movement/
│   └── exfiltration/
├── pipelines/          # per-customer field mappings
├── tests/              # known-positive / known-negative samples
└── .github/workflows/  # sigma check → convert → test → deploy
```

CI should, at minimum: `sigma check` every rule, convert against every target
backend the estate uses, and fail the build on conversion errors. Deployment to
production stays behind human sign-off.

---

## Coverage, honestly

Map rules to ATT&CK (see `attack-mapping`) and visualise gaps in the ATT&CK
Navigator.

But treat coverage counts sceptically: **ten rules for one technique is not
ten times the coverage.** Count techniques where you have a *tested* detection
with a known FP profile and a validated known-positive. That number is usually
much smaller than the rule count, and it is the honest one to report to a
customer.

---

## Pitfalls

- Deploying a converted rule without a known-positive test
- Filtering on attacker-controllable fields
- Using Sigma's generic field names without a pipeline
- Reusing a rule `id` after a rewrite — breaks all downstream correlation
- Writing rules for techniques the customer has no log source for
- `level: critical` on everything

---

## Verification

- [ ] `sigma check` passes
- [ ] Converted for every backend in the estate, versions recorded
- [ ] Field mappings confirmed against the real schema
- [ ] Known-positive sample matches; known-negative does not
- [ ] Query runtime measured and within budget
- [ ] `falsepositives` written from observation
- [ ] ATT&CK tags present and correct
- [ ] Rule `id` is a fresh, stable UUID
