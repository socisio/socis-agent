---
title: "Performing Cloud Forensics With Aws Cloudtrail — Investigate AWS account compromise by querying CloudTrail"
sidebar_label: "Performing Cloud Forensics With Aws Cloudtrail"
description: "Investigate AWS account compromise by querying CloudTrail"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Performing Cloud Forensics With Aws Cloudtrail

Investigate AWS account compromise by querying CloudTrail

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/performing-cloud-forensics-with-aws-cloudtrail` |
| Path | `optional-skills/security/performing-cloud-forensics-with-aws-cloudtrail` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `cloud-security`, `aws`, `cloudtrail`, `forensics`, `incident-response`, `dfir`, `boto3`, `s3` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Performing Cloud Forensics with AWS CloudTrail

## When to Use

- When investigating suspected AWS account compromise
- After detecting unauthorized API calls or credential exposure
- During incident response involving cloud infrastructure
- When analyzing S3 data exfiltration or IAM privilege escalation
- For post-incident forensic timeline reconstruction

## Prerequisites

- AWS account with CloudTrail enabled (management and data events)
- IAM permissions for cloudtrail:LookupEvents, s3:GetObject, athena:StartQueryExecution
- boto3 Python SDK installed
- CloudTrail logs delivered to S3 with optional Athena table configured
- AWS CLI configured with appropriate credentials

## Workflow

1. **Scope Investigation**: Identify timeframe, affected accounts, and compromised credentials.
2. **Query CloudTrail**: Use boto3 lookup_events or Athena to retrieve relevant API events.
3. **Filter by Indicators**: Search for suspicious user agents, source IPs, and event names.
4. **Reconstruct Timeline**: Build chronological sequence of attacker actions from API calls.
5. **Analyze Access Patterns**: Identify data access, IAM changes, and resource modifications.
6. **Identify Persistence**: Check for new IAM users, access keys, roles, or Lambda functions.
7. **Generate Report**: Produce forensic timeline with findings and remediation steps.

## Key Concepts

| Concept | Description |
|---------|-------------|
| LookupEvents | CloudTrail API to query management events (last 90 days) |
| Athena Queries | SQL queries against CloudTrail logs in S3 for historical analysis |
| User Agent Analysis | Identify tool signatures (AWS CLI, SDK, console, custom) |
| AccessKeyId | Track activity by specific IAM access key |
| EventName | AWS API action name (e.g., GetObject, CreateUser, AssumeRole) |
| sourceIPAddress | Origin IP of API call for geolocation analysis |

## Tools & Systems

| Tool | Purpose |
|------|---------|
| boto3 CloudTrail client | Programmatic CloudTrail event lookup |
| AWS Athena | SQL-based analysis of CloudTrail S3 logs |
| AWS CLI | Command-line CloudTrail queries |
| jq | JSON processing for CloudTrail event parsing |
| CloudTrail Lake | Advanced event data store with SQL query support |

## Output Format

```
Forensic Report: AWS-IR-[DATE]-[SEQ]
Account: [AWS Account ID]
Timeframe: [Start] to [End]
Compromised Credentials: [Access Key IDs]
Suspicious Events: [Count]
Source IPs: [List of attacker IPs]
Actions Taken: [API calls by attacker]
Data Accessed: [S3 objects, secrets, etc.]
Persistence Mechanisms: [New users, keys, roles]
```
