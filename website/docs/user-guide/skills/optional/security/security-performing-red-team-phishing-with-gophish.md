---
title: "Performing Red Team Phishing With Gophish — Automates GoPhish phishing simulation campaigns using the"
sidebar_label: "Performing Red Team Phishing With Gophish"
description: "Automates GoPhish phishing simulation campaigns using the"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Performing Red Team Phishing With Gophish

Automates GoPhish phishing simulation campaigns using the

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/performing-red-team-phishing-with-gophish` |
| Path | `optional-skills/security/performing-red-team-phishing-with-gophish` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `red-teaming`, `phishing-simulation`, `gophish`, `social-engineering`, `campaign-automation`, `security-awareness` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

## When to Use

- When conducting security assessments that involve performing red team phishing with gophish
- When following incident response procedures for related security events
- When performing scheduled security testing or auditing activities
- When validating security controls through hands-on testing

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

1. Install dependencies: `pip install gophish requests`
2. Deploy GoPhish server and obtain an API key from Settings.
3. Use the Python gophish library to automate campaign setup:
   - Create email templates with HTML body and tracking
   - Configure SMTP sending profiles
   - Import target groups from CSV
   - Create landing pages for credential capture
   - Launch and monitor campaigns
4. Analyze campaign results: opens, clicks, submitted data, reported.

```bash
# For authorized penetration testing and lab environments only
python scripts/agent.py --gophish-url https://localhost:3333 --api-key <key> --campaign-name "Q1 Awareness" --output phishing_report.json
```

## Examples

### Create Campaign via API
```python
from gophish import Gophish
from gophish.models import Campaign, Template, Group, SMTP, Page
api = Gophish("api_key", host="https://localhost:3333", verify=False)  # Self-signed cert on localhost lab
campaign = Campaign(name="Q1 Test", groups=[Group(name="Sales Team")],
    template=Template(name="IT Password Reset"), smtp=SMTP(name="Internal SMTP"),
    page=Page(name="Credential Page"))
api.campaigns.post(campaign)
```
