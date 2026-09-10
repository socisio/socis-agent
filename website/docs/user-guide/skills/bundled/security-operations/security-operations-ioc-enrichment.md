---
title: "Ioc Enrichment — Enrich an IOC across connected intel sources, or answer questions on enrichment order and pivoting"
sidebar_label: "Ioc Enrichment"
description: "Enrich an IOC across connected intel sources, or answer questions on enrichment order and pivoting"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Ioc Enrichment

Enrich an IOC across connected intel sources, or answer questions on enrichment order and pivoting.

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/security-operations/ioc-enrichment` |
| Version | `1.0.0` |
| Author | SOCIS |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Security`, `SOC`, `ThreatIntel`, `Enrichment`, `MCP` |
| Related skills | [`alert-triage`](/user-guide/skills/bundled/security-operations/security-operations-alert-triage), [`attack-mapping`](/user-guide/skills/bundled/security-operations/security-operations-attack-mapping), [`incident-response`](/user-guide/skills/bundled/security-operations/security-operations-incident-response) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# IOC Enrichment

Take one indicator, ask every intel source that is connected, and return a
single correlated verdict.

This is the pattern that makes MCP servers worth connecting. Invoking one
tool by hand — `get_cve_details CVE-2024-3400` — answers one question from
one vendor. The analyst's actual question is *"should I care about this?"*,
and that needs several sources agreeing or disagreeing.

---

## Guardrails

1. **Never submit customer data to a public sandbox.** A hash is fine. A
   file, a URL containing a session token, or an internal hostname is not —
   uploading those to VirusTotal publishes them. Ask before submitting
   anything that is not already public.
2. **A clean result is not an answer.** Novel and targeted malware is clean
   by definition. Say "no detections" and mean it literally; do not translate
   it to "benign".
3. **Name the source of every claim.** "VirusTotal: 3/71" and "our MISP has
   this in event 4412" are different weights of evidence and the reader needs
   to know which is which.
4. **Say which sources were unavailable.** A verdict built on two of five
   sources is a different thing from one built on five, and the reader cannot
   tell unless you say so.
5. **One tenant at a time.** Never carry an observable from one customer's
   investigation into another's.
6. **The headline verdict must answer the question that was asked.** "Is it
   safe to allow through the firewall?" wants an allow/block call, not a
   reputation score. The analyst acts on the first line; a correct analysis
   underneath a wrong headline is a wrong answer. If the honest verdict is
   "insufficient evidence", lead with that.
7. **Reserved, bogon and documentation ranges are BLOCK-and-investigate, never
   allow.** RFC 1918, RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`,
   `203.0.113.0/24`), RFC 6598, loopback, link-local and multicast have no
   business as a source on a perimeter link. Every reputation service will
   report them as clean and whitelisted, because there is nothing to report —
   and that is not a reason to permit them. Seeing one in live traffic means
   spoofing, a misconfigured device, or a sensor writing the wrong field, and
   that is the finding worth escalating.

   Any abuse report against such an address is itself evidence of
   misattribution: a non-routable IP cannot have attacked anything. Say so
   rather than repeating the report.

---

## Which sources to ask

Ask whatever is connected. Do not fail because something is missing — note
it and continue.

| Source | MCP server | Ask it for |
|---|---|---|
| Internal intel | MISP, OpenCTI | Have *we* seen this before? Which event, which actor? |
| Commercial intel | ThreatStream / Anomali | Actor attribution, campaign, confidence |
| Reputation | VirusTotal | Detection ratio, first seen, relationships |
| Infrastructure | Shodan | Open ports, certs, what else lives there |
| Vulnerability | NVD (`nvd`) | CVSS, CWE, affected versions |
| Exploitation | **built-in** `cve-intel` | Is a CVE actually being exploited, and how likely |
| Lookalike domains | **built-in** `domain-intel` | Is this domain a typosquat of a brand we protect |
| Own telemetry | Splunk, Wazuh, Elastic | **Has this appeared in our environment?** |

The last row is the one analysts forget and the one that changes the answer.
Reputation data says whether an indicator is bad in general; your own
telemetry says whether it is *your* problem.

Start with `tools_list` (or the Tools tab) to see what is actually connected
before planning the fan-out.

**Two of these need no MCP server and no API key.** `cve-intel` and
`domain-intel` are built in, so they are always available even when a customer
has nothing connected:

- **Any CVE in the indicator set** → `exploitation_triage`. CVSS says how bad
  it could be; KEV says whether it is being exploited; EPSS says how likely
  that is next month. A CVSS 9.8 with no KEV entry and 0.02% EPSS is
  theoretically severe and practically ignorable this week, and reporting it as
  urgent costs credibility.
- **Any domain that resembles a brand you protect** → `domain_permutations`.
  A lookalike that resolves to infrastructure the brand does not own is a
  finding; one on a registrar parking range usually is not.

---

## Procedure

### 1. Classify the indicator

Route by type — asking Shodan about a file hash wastes a call and returns
nothing useful.

```
IPv4/IPv6   → reputation, infrastructure, own telemetry
Domain/FQDN → reputation, passive DNS, cert transparency, own telemetry
URL         → reputation, sandbox (see guardrail 1)
File hash   → reputation, malware family, own telemetry
CVE ID      → vulnerability detail, exploit status, own asset exposure
Email       → sender reputation, header analysis, own mail telemetry
```

### 2. Fan out

Query every applicable connected source. Run them together where possible —
these are independent lookups and serialising them just makes the analyst
wait.

Record for each: the source, what it returned, and when the data is from.
Intel ages; a "last seen" from eight months ago is a different fact from one
from yesterday.

### 3. Check your own environment

Always, even when external sources say the indicator is clean:

```spl
index=* <indicator> earliest=-90d | stats count by index, sourcetype, host
```
```kql
search "<indicator>" | where TimeGenerated > ago(90d)
| summarize count() by Type, Computer
```

**A clean indicator that appears in your logs is more interesting than a
malicious one that does not.**

### 4. Correlate

Sources will disagree. That is information, not a problem:

- **All agree malicious** → high confidence, act
- **Internal intel hits, external clean** → likely targeted, or your own
  historical finding. Weight internal higher.
- **External hits, internal clean** → known-bad infrastructure you have not
  encountered. Blocklist candidate, not an incident.
- **Only reputation hits, on shared infrastructure** → probably meaningless.
  Check what else resolves there before escalating.
- **Everything clean but it is in your telemetry** → the interesting case.
  Investigate the behaviour, not the indicator.

### 5. Report

```markdown
## IOC Enrichment — <indicator>

**Type:** <ip|domain|hash|cve|url>   **Tenant:** <customer>
**Verdict:** MALICIOUS | SUSPICIOUS | BENIGN | INSUFFICIENT EVIDENCE
**Confidence:** High | Medium | Low

### Sources consulted
| Source | Result | Data age |
|---|---|---|
| VirusTotal | 3/71 detections | first seen 2026-08-14 |
| MISP | event 4412, APT-x campaign | 2026-06-02 |
| Splunk | 14 hits, 2 hosts, last 6d | live |

### Present in our environment
<hosts, accounts, timeframe — or "no telemetry hits in 90d">

### Assessment
<why the verdict follows from the rows above>

### Sources unavailable
<which were not connected or did not respond — this is not optional>

### Recommended action
<block / hunt / monitor / no action>
```

---

## Why this beats calling tools directly

`/get_cve_details CVE-2024-3400` returns a CVSS score. Useful, but it is a
lookup, and the analyst already had to know which tool and which argument.

Asking *"is CVE-2024-3400 something we need to worry about?"* runs this
skill: NVD for severity, ThreatStream for exploitation in the wild, the SIEM
for whether you even run the affected product, and the CMDB for how exposed
those assets are. Then one answer.

That is the difference between a tool and an agent, and it is why the tools
are better as a capability the agent composes than as 200 slash commands the
analyst has to memorise.

---

## Pitfalls

- Treating a clean VirusTotal score as a verdict
- Skipping the internal-telemetry check because external sources looked clear
- Reporting a verdict without saying which sources were down
- Enriching shared infrastructure (CDNs, cloud egress) and escalating the hit
- Submitting internal URLs or files to public sandboxes
- Asking every source about every indicator type regardless of relevance

---

## Verification

- [ ] Indicator type classified and sources routed accordingly
- [ ] Every connected source queried, not just the fastest one
- [ ] Own telemetry checked regardless of external results
- [ ] Every claim attributed to a named source with a data age
- [ ] Unavailable sources listed explicitly
- [ ] Verdict follows from the evidence table, not from one source
- [ ] Nothing customer-identifying submitted to a public service
