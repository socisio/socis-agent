---
title: "Attack Mapping — Map observed activity to MITRE ATT&CK; assess real coverage"
sidebar_label: "Attack Mapping"
description: "Map observed activity to MITRE ATT&CK; assess real coverage"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Attack Mapping

Map observed activity to MITRE ATT&CK; assess real coverage.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/security-operations/attack-mapping` |
| Version | `1.0.0` |
| Author | SOCIS |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Security`, `MITRE`, `ATTACK`, `ThreatIntel` |
| Related skills | [`alert-triage`](/docs/user-guide/skills/bundled/security-operations/security-operations-alert-triage), [`detection-engineering`](/docs/user-guide/skills/bundled/security-operations/security-operations-detection-engineering), [`incident-response`](/docs/user-guide/skills/bundled/security-operations/security-operations-incident-response) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# ATT&CK Mapping

Mapping observed adversary behaviour to MITRE ATT&CK, and assessing detection
coverage honestly.

ATT&CK is useful for two things: giving analysts and customers a shared
vocabulary, and exposing what you *cannot* see. It is not a scoreboard.

---

## Guardrails

1. **Map behaviour, not tool names.** "They used Mimikatz" is not a mapping.
   *What did it do* — dumped LSASS memory (T1003.001) — is.
2. **Do not over-map.** Assigning six techniques to one observation inflates
   apparent sophistication and misleads the reader.
3. **Only map what you observed.** Not what the malware family *usually* does.
   If you infer, label it as inference.
4. **Sub-techniques when you can support them.** T1003 is vague; T1003.001 is
   actionable. But do not guess a sub-technique to look precise.
5. **Coverage ≠ detection.** A rule that exists is not a rule that works. See
   below.

---

## Structure

<!-- ascii-guard-ignore -->
```
Tactic      the adversary's goal          (TA0006 — Credential Access)
 └ Technique   how they achieve it        (T1003 — OS Credential Dumping)
    └ Sub-technique   the specific method (T1003.001 — LSASS Memory)
```
<!-- ascii-guard-ignore-end -->

**14 Enterprise tactics**, roughly in attack order:

| ID | Tactic | Goal |
|---|---|---|
| TA0043 | Reconnaissance | Gather target information |
| TA0042 | Resource Development | Build/acquire infrastructure |
| TA0001 | Initial Access | Get in |
| TA0002 | Execution | Run code |
| TA0003 | Persistence | Survive reboot/credential change |
| TA0004 | Privilege Escalation | Gain higher permissions |
| TA0005 | Defense Evasion | Avoid detection |
| TA0006 | Credential Access | Steal credentials |
| TA0007 | Discovery | Learn the environment |
| TA0008 | Lateral Movement | Move between systems |
| TA0009 | Collection | Gather target data |
| TA0011 | Command and Control | Communicate with implants |
| TA0010 | Exfiltration | Steal data out |
| TA0040 | Impact | Destroy, disrupt, extort |

Separate matrices exist for **Mobile**, **ICS**, and cloud/container platforms
within Enterprise. Use the right one — mapping an OT incident to Enterprise
misses the techniques that matter.

---

## Mapping procedure

1. **Describe the behaviour** in a neutral sentence, without tool names.
   *"A process read the memory of lsass.exe and wrote it to disk."*
2. **Identify the goal** → tactic. Reading LSASS is about obtaining
   credentials → Credential Access.
3. **Find the technique** — search ATT&CK for the behaviour.
4. **Go to sub-technique** only if the evidence supports it.
5. **Record the evidence** alongside the mapping. A mapping without a
   supporting observable is an opinion.

```markdown
| # | Observed | Tactic | Technique | Evidence | Confidence |
|---|---|---|---|---|---|
| 1 | rundll32 read lsass memory, wrote C:\t\d.dmp | Credential Access | T1003.001 | EDR proc event 14:22:07Z | High |
| 2 | New svc "SysUpdate" → C:\ProgramData\su.exe | Persistence | T1543.003 | EventID 7045 | High |
| 3 | Beacon to 185.x.x.x:443, 60s ±10% jitter | C2 | T1071.001 | Firewall logs | Medium |
```

**Confidence matters.** High = directly observed. Medium = strongly implied by
artifacts. Low = inferred from tooling or reporting. Never present Low as fact.

---

## Coverage assessment — the honest version

The standard approach — count rules per technique, colour the Navigator layer
green, present it — is misleading and customers increasingly know it.

A technique is only genuinely covered when **all** of these hold:

| Requirement | Question |
|---|---|
| **Log source** | Is the required telemetry actually collected? |
| **Retention** | Is it kept long enough to investigate? |
| **Detection** | Does a rule exist? |
| **Tested** | Has a known-positive been validated against it? |
| **FP profile** | Is the false-positive rate known and acceptable? |
| **Routing** | Does the alert reach a human who acts on it? |

Fail any one and it is not coverage. The most common failure is the first:
**writing detections for techniques where the log source was never onboarded.**
Check telemetry before writing rules.

Report coverage in three honest buckets rather than a percentage:

- **Covered** — all six criteria met, evidence available
- **Partial** — detection exists but untested, noisy, or telemetry is incomplete
- **Gap** — no telemetry or no detection

### Prioritising gaps

Do not chase full-matrix coverage; nobody has it and pursuing it wastes budget.
Prioritise by:

1. **Threat-informed** — what do the groups actually targeting this customer's
   sector use? Start from ATT&CK group pages and current reporting.
2. **Chokepoints** — techniques that appear in most intrusion chains regardless
   of actor. Credential dumping, valid accounts, remote services, scheduled
   tasks.
3. **Impact** — techniques that would be catastrophic if missed.

Ten well-tested detections on chokepoint techniques beat two hundred untested
rules spread across the matrix.

---

## Navigator layers

```json
{
  "name": "Coverage — <customer>",
  "versions": {"attack": "17", "navigator": "5.1.0", "layer": "4.5"},
  "domain": "enterprise-attack",
  "techniques": [
    {"techniqueID": "T1003.001", "score": 3, "comment": "Tested, FP rate <1/wk"},
    {"techniqueID": "T1071.001", "score": 2, "comment": "Rule exists, untested"},
    {"techniqueID": "T1547.001", "score": 1, "comment": "No registry telemetry"}
  ],
  "gradient": {"colors": ["#e5e5e5", "#ff3366", "#ffc107", "#4caf50"], "minValue": 0, "maxValue": 3}
}
```

Scoring `0=none, 1=gap, 2=partial, 3=covered`. Put the *reason* in the comment
— a layer without comments cannot be acted on later, including by you.

Pin the ATT&CK version. Techniques get added, deprecated and renumbered; an
undated layer becomes unreadable within a year.

---

## Using ATT&CK across the workflow

- **Triage** — map the alert; the tactic tells you what the adversary was
  trying to *achieve*, which suggests what to check next
- **IR** — map as you scope; gaps in the chain point at activity you have not
  found yet. An intrusion with Initial Access and Impact but nothing between
  means you are missing the middle, not that it did not happen
- **Detection engineering** — tag every rule; makes coverage measurable
- **Reporting** — gives customers a vocabulary comparable across vendors

---

## Pitfalls

- Mapping tools instead of behaviours
- Inflating technique counts to look thorough
- Presenting inference as observation
- Reporting rule counts as coverage
- Writing detections for techniques with no telemetry
- Undated Navigator layers
- Chasing matrix completeness over chokepoint depth
- Using Enterprise for ICS/OT incidents

---

## Verification

- [ ] Each mapping cites a specific observable
- [ ] Confidence stated; inference labelled as such
- [ ] Sub-techniques used only where evidence supports them
- [ ] Correct matrix for the environment
- [ ] Coverage claims verified against actual telemetry, not rule counts
- [ ] Navigator layer versioned and commented
- [ ] Gaps prioritised by threat relevance, not matrix completeness
