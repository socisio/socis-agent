---
name: incident-response
description: "Run an incident: contain, eradicate, recover, report."
version: 1.0.0
author: SOCIS
license: MIT
platforms: [linux, macos, windows]
category: security-operations
triggers:
  - "we have an incident"
  - "incident response"
  - "we've been breached"
  - "ransomware"
  - "contain this"
  - "incident report"
  - "post-incident review"
toolsets:
  - terminal
  - file
  - web
metadata:
  socis:
    tags: [Security, IncidentResponse, NIST, DFIR]
    related_skills: [alert-triage, evidence-handling, attack-mapping]
---

# Incident Response

Running a confirmed incident from declaration to closure.

Aligned to **NIST SP 800-61r3** (April 2025), which restructures incident
response around the CSF 2.0 functions — Govern, Identify, Protect, Detect,
Respond, Recover.

> **Note on the standard.** SP 800-61 **Rev 2 was formally withdrawn in April
> 2025**. Its familiar four-phase lifecycle is still a good way to *think and
> train*, and this skill follows that operational shape — but cite **Rev 3** in
> anything a customer, auditor, or regulator will read. Citing withdrawn
> guidance in a deliverable is an easy and avoidable finding.

---

## Guardrails

1. **Preserve before you contain.** Containment destroys volatile evidence.
   Capture RAM and volatile state first unless active damage makes that
   indefensible — and if you skip it, record *why*.
2. **Do not tip off the adversary.** Blocking one C2 domain on a live intrusion
   teaches them you are watching and triggers fallback channels. Scope fully,
   then contain everything at once.
3. **The customer decides business trade-offs.** Isolating a production system
   is their call, not yours. Present options and consequences; do not
   unilaterally take a business offline.
4. **Notification clocks may already be running.** GDPR is 72 hours from
   awareness. Other regimes differ. Raise this at declaration — not at closure.
5. **Do not negotiate with or pay ransomware actors on a customer's behalf.**
   Sanctions exposure is real. That decision belongs to the customer, their
   counsel, and their insurer.
6. **Assume the write-up will be read adversarially.**

---

## Phase 1 — Declare and organise

**Declaration** is a deliberate act. Record: who declared, when (UTC), on what
basis. This timestamp anchors every notification deadline.

Assign explicitly — ambiguity here is the most common cause of chaotic
response:

| Role | Owns |
|---|---|
| Incident Commander | Decisions, priorities. **Not doing technical work.** |
| Technical Lead | Investigation and containment execution |
| Scribe | Contemporaneous timeline |
| Comms Lead | Customer, internal, regulator, law enforcement |
| Customer Liaison | Their authority to approve business-impacting actions |

**Set up out-of-band comms.** If the corporate estate may be compromised, the
incident channel cannot live on it. Assume email and chat are read by the
adversary until proven otherwise.

Open the case with an ID and start the evidence log now (`evidence-handling`).

### Severity

Set it from **business impact**, not technical novelty:

| | Criteria |
|---|---|
| **Critical** | Active data exfiltration, ransomware encrypting, safety systems, or full domain compromise |
| **High** | Confirmed unauthorised access to sensitive systems; contained but active adversary |
| **Medium** | Limited scope, no data access confirmed, adversary appears gone |
| **Low** | Policy violation, near-miss, malware blocked before execution |

---

## Phase 2 — Scope before you act

**The most common failure in IR is containing what you can see and missing what
you cannot.** Partial containment tells the adversary you are onto them and
leaves their persistence intact.

Establish, before touching anything:

- **Patient zero** — first affected asset, and initial access vector
- **Timeline** — first activity to now, in UTC
- **Lateral movement** — every host and account touched
- **Persistence** — services, scheduled tasks, registry, WMI subscriptions,
  cron, startup, SSH keys, OAuth grants, mail rules, IAM changes
- **Credential exposure** — what could have been harvested from memory, LSASS,
  browser stores, key vaults, CI/CD secrets
- **Data accessed** — what, how much, and did it leave

Hunt for each observable across the estate, not only where the alert fired.
Detection exists where you deployed it; the adversary is not limited to that.

Map to ATT&CK as you go (`attack-mapping`) — it surfaces techniques you have
not checked for yet.

---

## Phase 3 — Contain

Preserve volatile evidence first. Then contain **everything at once**.

**Short-term** (stop the bleeding):
- Network isolation — keep the host powered on
- Disable compromised accounts; revoke sessions and tokens (a disabled account
  with a live refresh token is not contained)
- Block C2 at egress
- Rotate exposed credentials, including service accounts and API keys

**Longer-term** (adversary out, business running):
- Rebuild rather than clean — a "cleaned" host is not trustworthy
- Patch or remove the initial access vector
- Enforce MFA on everything reachable
- Segment to stop the next lateral hop

**Ransomware specifics:**
- Do **not** power off — decryption keys may be in RAM
- Preserve ransom notes and a sample encrypted file
- Check no-more-ransom.org before assuming payment is the only option
- Verify backups are *clean and restorable* before relying on them; the
  adversary probably targeted them
- Payment is a customer/counsel/insurer decision, with sanctions implications

---

## Phase 4 — Eradicate and recover

Eradication ends when **you can state where the adversary got in and prove that
path is closed.** Removing malware without closing the vector guarantees
re-entry.

Recovery:
1. Restore from a backup verified clean and predating compromise
2. Rebuild from known-good images; do not reuse the compromised system
3. Rotate all credentials that were, or plausibly were, exposed
4. **Monitor at elevated intensity.** Re-intrusion within days is common
5. Return to production in stages, watching each

Define exit criteria before starting — otherwise "recovered" becomes a feeling
rather than a finding.

---

## Phase 5 — Report and improve

### Customer report

```markdown
# Incident Report — <case ID>

**Customer:** <name>   **Classification:** <TLP:AMBER etc.>
**Declared:** <UTC>   **Contained:** <UTC>   **Closed:** <UTC>
**Severity:** <level>

## Executive summary
<Plain language. What happened, what was affected, what was done, current
status. No jargon — this is read by people who are not engineers.>

## Timeline
| UTC | Event | Evidence ref |
|---|---|---|

## Initial access
<Vector, with evidence. If unknown, say so plainly.>

## Scope
Systems: <list>   Accounts: <list>   Data: <what was accessed or exfiltrated>

## Adversary activity (ATT&CK)
| Tactic | Technique | Observed as |
|---|---|---|

## Response actions
| UTC | Action | By | Outcome |
|---|---|---|---|

## Current status
<Contained? Eradicated? Residual risk?>

## Evidence
<Items held, hashes, retention period.>

## Recommendations
| Priority | Recommendation | Addresses |
|---|---|---|

## Unknowns
<What could not be determined and why — missing logs, expired retention,
destroyed evidence.>
```

The **Unknowns** section is mandatory. Every real incident has them. A report
without unknowns reads as either incurious or dishonest, and it is the section
a competent reviewer checks first.

### Post-incident review

Hold it within two weeks, while memory is fresh. **Blameless** — you are
looking for systemic gaps, not individuals.

- What worked? What did not?
- What did we not have that we needed? (log source, tooling, access, authority)
- How long from compromise to detection, and why?
- What detection would have caught this earlier? → `detection-engineering`
- Which recommendations are the customer actually going to fund?

Track the actions to closure. A review that generates recommendations nobody
owns is theatre.

---

## Notification

Raise at declaration, not at closure. Clocks start at **awareness**, and the
declaration timestamp is what gets scrutinised.

| Regime | Typical trigger | Deadline |
|---|---|---|
| GDPR | Personal data breach, risk to individuals | 72h to supervisory authority |
| HIPAA | PHI breach | 60 days; ≥500 records also to media |
| PCI DSS | Cardholder data | Immediately, per brand rules |
| SEC | Material incident (US public companies) | 4 business days |
| Contractual | Per MSA — often much tighter | Check the contract |

This table is orientation, not legal advice. Requirements vary by jurisdiction
and change. Counsel decides.

---

## Pitfalls

- Containing before scoping — adversary adapts, persistence survives
- Powering off and losing RAM
- Cleaning instead of rebuilding
- Restoring from a backup that was also compromised
- Missing persistence: OAuth grants, mail forwarding rules, IAM roles, CI/CD
  secrets — all commonly overlooked
- Incident channel on possibly-compromised infrastructure
- Incident Commander doing hands-on work and losing situational awareness
- Discovering notification obligations after the deadline
- Declaring closed without stating residual risk

---

## Verification

- [ ] Declaration time recorded; notification obligations assessed
- [ ] Roles assigned; comms out-of-band if warranted
- [ ] Evidence preserved before containment, or the deviation justified
- [ ] Scope established before containment
- [ ] Initial access vector identified and closed — or explicitly unknown
- [ ] All persistence mechanisms hunted, not just the obvious ones
- [ ] Credentials rotated
- [ ] Backups verified clean before restore
- [ ] Elevated monitoring in place post-recovery
- [ ] Report includes an honest Unknowns section
- [ ] Post-incident review scheduled with owned actions
