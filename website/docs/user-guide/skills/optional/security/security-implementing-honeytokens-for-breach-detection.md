---
title: "Implementing Honeytokens For Breach Detection — Deploys canary tokens and honeytokens (fake AWS"
sidebar_label: "Implementing Honeytokens For Breach Detection"
description: "Deploys canary tokens and honeytokens (fake AWS"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Implementing Honeytokens For Breach Detection

Deploys canary tokens and honeytokens (fake AWS

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/implementing-honeytokens-for-breach-detection` |
| Path | `optional-skills/security/implementing-honeytokens-for-breach-detection` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `deception-technology`, `honeytokens`, `canary-tokens`, `breach-detection`, `dns-canary`, `security-operations` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Implementing Honeytokens for Breach Detection


## When to Use

- When deploying or configuring implementing honeytokens for breach detection capabilities in your environment
- When establishing security controls aligned to compliance requirements
- When building or improving security architecture for this domain
- When conducting security assessments that require this implementation

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Deploy honeytokens across critical systems to detect unauthorized access. Each token
type alerts via webhook when triggered by an attacker.

```python
import requests

# Create a DNS canary token via Canarytokens
resp = requests.post("https://canarytokens.org/generate", data={
    "type": "dns",
    "email": "soc@company.com",
    "memo": "Production DB server honeytoken",
})
token = resp.json()
print(f"DNS token: {token['hostname']}")
```

Token types to deploy:
1. AWS credential files (~/.aws/credentials) with canary keys
2. DNS tokens embedded in configuration files
3. Document beacons (Word/PDF) in sensitive file shares
4. Database honeytoken records in user tables
5. Web bugs in internal wiki/documentation pages

## Examples

```python
# Generate a fake AWS credentials file with canary token
aws_creds = f"[default]\naws_access_key_id = {canary_key_id}\naws_secret_access_key = {canary_secret}\n"
with open("/opt/backup/.aws/credentials", "w") as f:
    f.write(aws_creds)
```
