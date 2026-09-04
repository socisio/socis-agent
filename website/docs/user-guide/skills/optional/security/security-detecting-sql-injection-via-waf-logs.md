---
title: "Detecting Sql Injection Via Waf Logs — Analyze WAF (ModSecurity/AWS WAF/Cloudflare) logs to detect"
sidebar_label: "Detecting Sql Injection Via Waf Logs"
description: "Analyze WAF (ModSecurity/AWS WAF/Cloudflare) logs to detect"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Detecting Sql Injection Via Waf Logs

Analyze WAF (ModSecurity/AWS WAF/Cloudflare) logs to detect

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/detecting-sql-injection-via-waf-logs` |
| Path | `optional-skills/security/detecting-sql-injection-via-waf-logs` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `waf-log-analysis`, `sql-injection-detection`, `modsecurity`, `aws-waf`, `cloudflare-waf`, `web-application-security` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Detecting SQL Injection via WAF Logs


## When to Use

- When investigating security incidents that require detecting sql injection via waf logs
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

1. Install dependencies: `pip install requests`
2. Collect WAF logs (ModSecurity audit log, AWS WAF JSON logs, or Cloudflare firewall events).
3. Run the agent to parse and analyze:
   - Detect SQLi payloads via 15+ regex patterns
   - Classify attacks by OWASP injection type (classic, blind, time-based, UNION-based)
   - Identify persistent attackers by IP clustering
   - Correlate multi-request injection campaigns
   - Calculate attack success probability based on response codes

```bash
python scripts/agent.py --log-file /var/log/modsec_audit.log --format modsecurity --output sqli_report.json
```

## Examples

### ModSecurity SQLi Detection
```
Rule 942100 triggered: SQL Injection Attack Detected via libinjection
URI: /api/users?id=1' UNION SELECT username,password FROM users--
Source IP: 203.0.113.42 (47 requests in 5 minutes)
Classification: UNION-based SQLi campaign
```
