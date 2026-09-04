---
title: "Alert Triage — Triage SOC alerts: enrich, scope, classify, verdict"
sidebar_label: "Alert Triage"
description: "Triage SOC alerts: enrich, scope, classify, verdict"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Alert Triage

Triage SOC alerts: enrich, scope, classify, verdict.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/security-operations/alert-triage` |
| Version | `1.0.0` |
| Author | SOCIS |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Security`, `SOC`, `Triage`, `DetectionResponse` |
| Related skills | [`attack-mapping`](/docs/user-guide/skills/bundled/security-operations/security-operations-attack-mapping), [`incident-response`](/docs/user-guide/skills/bundled/security-operations/security-operations-incident-response), [`evidence-handling`](/docs/user-guide/skills/bundled/security-operations/security-operations-evidence-handling) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Alert Triage

A repeatable L1/L2 workflow for turning a raw SIEM alert into a defensible
verdict: **true positive**, **false positive**, or **escalate**.

Platform-neutral by design. The analysis order is the same whether the alert
came from Splunk, Sentinel, Elastic, QRadar, Chronicle, or an EDR console —
only the query syntax changes.

---

## Guardrails — read before every triage

These exist because a confident wrong verdict is worse than no verdict.

1. **No verdict without evidence.** Every conclusion cites a specific
   observable: a log line, a hash, a process tree, a query result. "Looks like
   normal admin activity" is not a finding; "matches the scheduled Ansible run
   at 03:00 from 10.2.4.7, see query below" is.
2. **Absence of evidence is not evidence of absence.** If a log source was
   unavailable, say so explicitly in the verdict. Do not close an alert as FP
   because you could not find the data.
3. **Never modify the endpoint during triage.** Triage is read-only. If the
   situation needs containment, that is an escalation to `incident-response`,
   not something to do mid-triage.
4. **One customer at a time.** In a multi-tenant/MSSP context, never carry
   observables, queries, or context from one tenant into another's
   investigation. State the tenant explicitly at the start of the work.
5. **Say when you are unsure.** An honest "insufficient evidence, escalating
   for human review" is a valid and often correct outcome.

---

## When to Use

- A SIEM/EDR alert needs a verdict
- Someone asks "is this real?" about a detection
- A batch of low-severity alerts needs triaging for patterns

Do **not** use this for confirmed incidents — go to `incident-response`.

---

## Procedure

### Phase 0 — Frame the alert

Record before analysing anything:

| Field | Why |
|---|---|
| Tenant / customer | Multi-tenant isolation |
| Alert name + rule ID | Traceability back to the detection |
| Fired at (UTC) | Correlation across sources |
| Source platform | Determines query dialect |
| Severity as assigned | Compare against your own verdict later |
| Affected asset(s) | Scope anchor |
| Affected identity(s) | Scope anchor |

State the **detection logic in plain language** before looking at anything
else: *what behaviour did this rule intend to catch?* Many false positives are
obvious the moment the rule's intent is stated and clearly doesn't match what
happened.

### Phase 1 — Extract observables

Pull every observable from the alert:

- Hashes (MD5/SHA1/SHA256)
- IPs, domains, URLs
- File paths, process names, command lines
- User accounts, service principals, session IDs
- Registry keys, scheduled task names, service names

Keep them in a working list. These drive every subsequent query.

### Phase 2 — Enrich

Enrich each observable. Prefer sources the customer already licenses.

```
Hash        → VirusTotal, MalwareBazaar, internal allowlist, EDR reputation
IP/Domain   → passive DNS, WHOIS/RDAP age, ASN, threat intel feeds, GeoIP
Account     → directory role, MFA status, normal login geography/hours
Asset       → CMDB owner, criticality, patch level, exposure (internet-facing?)
Command line→ decode any encoding (base64/hex), LOLBAS lookup
```

**Enrichment caveats that cause bad verdicts:**

- A clean VirusTotal score does **not** mean benign. Novel and targeted malware
  is clean by definition. Low detection count on a *recently submitted* sample
  is much weaker evidence than low count on an old one.
- A high VT score on a **system binary** usually means someone submitted a
  packed copy, not that the local file is malicious. Check the hash matches the
  vendor's known-good.
- Threat intel hits on **shared infrastructure** (CDNs, cloud egress ranges,
  popular hosting) are frequently meaningless. Check what else lives on that IP.

### Phase 3 — Establish a baseline

The core triage question is almost always: **is this normal for this
environment?**

Answer it with data, not intuition:

- Has this binary/command run on this host before? How often?
- Has this account logged in from this location/device before?
- Do peer assets in the same role show the same behaviour?
- Does the timing match a known change window, backup job, or deployment?

A behaviour that is rare **and** unexplained is far more interesting than one
that is merely unusual-looking.

### Phase 4 — Scope

If the behaviour looks genuinely suspicious, establish blast radius **before**
declaring a verdict:

- Same observable on other hosts?
- Same account active elsewhere?
- Same parent process or delivery vector elsewhere?
- Any outbound connections following the activity?

Scope changes severity. A single host is a triage outcome; twenty hosts is an
incident.

### Phase 5 — Map and verdict

Map the observed behaviour to ATT&CK (see the `attack-mapping` skill) — this
makes the finding communicable and comparable.

Then reach one of three verdicts:

**TRUE POSITIVE** — malicious or unauthorised activity confirmed.
→ Escalate to `incident-response`. Do not begin containment from triage.

**FALSE POSITIVE** — benign activity that matched the rule.
→ Document *why* it is benign, and record a **detection improvement**: what
rule change would have prevented this alert without losing coverage? An FP that
generates no tuning feedback will fire again next week.

**INCONCLUSIVE / ESCALATE** — insufficient evidence.
→ State exactly what data was missing and what would settle it. This is a
legitimate outcome; forcing a verdict without evidence is not.

---

## Output format

Write the verdict in this shape so it is consistent across analysts and
readable by the customer:

```markdown
## Alert Triage — <alert name>

**Tenant:** <customer>
**Alert:** <rule name / ID>   **Fired:** <UTC timestamp>
**Asset:** <hostname / resource>   **Identity:** <account>
**Verdict:** TRUE POSITIVE | FALSE POSITIVE | ESCALATE
**Severity (assessed):** Critical | High | Medium | Low
**ATT&CK:** T#### — <technique name>

### What fired and why
<the rule's intent, in plain language>

### What actually happened
<the reconstructed sequence of events, with timestamps>

### Evidence
| # | Observable | Source | Finding |
|---|---|---|---|
| 1 | <hash/IP/cmdline> | <query or feed> | <what it showed> |

### Scope
<hosts/accounts affected, or "contained to single host">

### Verdict rationale
<why this conclusion follows from the evidence above>

### Gaps
<log sources unavailable, data outside retention, unanswered questions>

### Recommended actions
<containment / tuning / no action>
```

The **Gaps** section is not optional. It is what separates a defensible
verdict from a guess, and it is the first thing a customer's auditor will look
for.

---

## Query translation

Analysts work across platforms. The same logical question in five dialects:

**"Did this hash execute anywhere in the last 7 days?"**

```spl
| tstats count where index=edr Processes.process_hash="<SHA256>" earliest=-7d
    by Processes.dest Processes.user Processes._time
```
```kql
DeviceProcessEvents
| where TimeGenerated > ago(7d) and SHA256 == "<SHA256>"
| project TimeGenerated, DeviceName, AccountName, ProcessCommandLine
```
```
process.hash.sha256: "<SHA256>" and @timestamp >= now-7d
```
```sql
SELECT * FROM events WHERE "SHA256 Hash" = '<SHA256>' LAST 7 DAYS
```

Do not assume a field name exists — schema varies by deployment and by how the
log source was onboarded. Confirm the field before trusting an empty result: an
empty result from a wrong field name looks identical to genuine absence.

---

## Pitfalls

- **Closing on a single enrichment source.** One clean VT score is not a
  verdict.
- **Confusing rare with malicious.** New software is rare. So is a new admin.
- **Ignoring the alert's own logic.** Read the rule before judging the alert.
- **Silently accepting empty query results.** Verify the query would return
  data at all — wrong index, wrong field name, and outside-retention all look
  like "nothing found."
- **Timezone drift.** Correlate in UTC. Mixed-timezone timelines produce
  confident wrong conclusions.
- **Tunnel vision on the alerting host.** The alert fires where detection
  exists, not necessarily where the activity started.

---

## Verification

Before submitting a verdict, confirm:

- [ ] Every claim in the write-up traces to a specific piece of evidence
- [ ] Queries were validated to return data (not silently empty)
- [ ] Baseline was checked, not assumed
- [ ] Scope was assessed beyond the alerting asset
- [ ] Gaps and missing log sources are stated
- [ ] Tenant is correct and no cross-tenant data appears
- [ ] FP verdicts include a concrete tuning recommendation
