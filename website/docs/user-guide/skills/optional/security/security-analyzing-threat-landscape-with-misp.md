---
title: "Analyzing Threat Landscape With Misp — Query a MISP (Malware Information Sharing Platform)"
sidebar_label: "Analyzing Threat Landscape With Misp"
description: "Query a MISP (Malware Information Sharing Platform)"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Analyzing Threat Landscape With Misp

Query a MISP (Malware Information Sharing Platform)

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/analyzing-threat-landscape-with-misp` |
| Path | `optional-skills/security/analyzing-threat-landscape-with-misp` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `threat-intelligence`, `misp`, `threat-landscape`, `ioc-analysis`, `cti`, `threat-sharing` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Analyzing Threat Landscape with MISP


## When to Use

- When investigating security incidents that require analyzing threat landscape with misp
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with threat intelligence concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

1. Install dependencies: `pip install pymisp`
2. Configure MISP URL and API key.
3. Run the agent to generate threat landscape analysis:
   - Pull event statistics by threat level and date range
   - Analyze attribute type distributions (IP, domain, hash, URL)
   - Identify top MITRE ATT&CK techniques from event tags
   - Track threat actor activity via galaxy clusters
   - Generate temporal trend analysis of IOC submissions

```bash
python scripts/agent.py --misp-url https://misp.local --api-key YOUR_KEY --days 90 --output landscape_report.json
```

## Examples

### Threat Landscape Summary
```
Period: Last 90 days
Events analyzed: 1,247
Top threat level: High (43%)
Top attribute type: ip-dst (31%), domain (22%), sha256 (18%)
Top MITRE technique: T1566 Phishing (89 events)
Top threat actor: APT28 (34 events)
```
