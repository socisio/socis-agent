---
title: "Implementing Web Application Logging With Modsecurity — Configure ModSecurity WAF with the OWASP Core Rule Set"
sidebar_label: "Implementing Web Application Logging With Modsecurity"
description: "Configure ModSecurity WAF with the OWASP Core Rule Set"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Implementing Web Application Logging With Modsecurity

Configure ModSecurity WAF with the OWASP Core Rule Set

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/implementing-web-application-logging-with-modsecurity` |
| Path | `optional-skills/security/implementing-web-application-logging-with-modsecurity` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `modsecurity`, `waf`, `crs`, `owasp`, `web-security`, `audit-logging`, `rule-tuning` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Implementing Web Application Logging with ModSecurity

## Overview

ModSecurity is an open-source WAF engine that works with Apache, Nginx, and IIS. The OWASP
Core Rule Set (CRS) provides generic attack detection rules covering SQL injection, XSS,
RCE, LFI, and other OWASP Top 10 attacks. ModSecurity logs full request/response data in
audit logs for forensic analysis and generates alerts that feed into SIEM platforms.


## When to Use

- When deploying or configuring implementing web application logging with modsecurity capabilities in your environment
- When establishing security controls aligned to compliance requirements
- When building or improving security architecture for this domain
- When conducting security assessments that require this implementation

## Prerequisites

- Web server (Apache 2.4+ or Nginx) with ModSecurity v3 module
- OWASP CRS v4.x installed
- Log aggregation infrastructure (ELK, Splunk, or Wazuh)

## Steps

1. Install ModSecurity and configure SecRuleEngine in DetectionOnly mode
2. Deploy OWASP CRS v4 and set paranoia level (PL1-PL4)
3. Configure SecAuditEngine for relevant-only logging
4. Tune false positives with SecRuleRemoveById and rule exclusions
5. Switch to blocking mode (SecRuleEngine On) after tuning period
6. Forward audit logs to SIEM for correlation and alerting

## Expected Output

```
ModSecurity: Warning. Pattern match "(?:union\s+select)" [file "/etc/modsecurity/crs/rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf"] [line "45"] [id "942100"] [msg "SQL Injection Attack Detected via libinjection"] [severity "CRITICAL"]
```
