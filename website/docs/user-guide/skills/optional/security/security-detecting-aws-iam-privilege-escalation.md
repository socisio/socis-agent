---
title: "Detecting Aws Iam Privilege Escalation — Detect AWS IAM privilege escalation paths using boto3 and"
sidebar_label: "Detecting Aws Iam Privilege Escalation"
description: "Detect AWS IAM privilege escalation paths using boto3 and"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Detecting Aws Iam Privilege Escalation

Detect AWS IAM privilege escalation paths using boto3 and

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/detecting-aws-iam-privilege-escalation` |
| Path | `optional-skills/security/detecting-aws-iam-privilege-escalation` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `aws`, `iam`, `privilege-escalation`, `cloudsplaining`, `boto3`, `policy-analysis`, `least-privilege` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Detecting AWS IAM Privilege Escalation

## Overview

This skill uses boto3 and Cloudsplaining-style analysis to identify IAM privilege escalation paths in AWS accounts. It downloads the account authorization details, analyzes each policy for dangerous permission combinations (iam:PassRole + lambda:CreateFunction, iam:CreatePolicyVersion, sts:AssumeRole), and flags policies that violate least-privilege principles.


## When to Use

- When investigating security incidents that require detecting aws iam privilege escalation
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Python 3.8+ with boto3 library
- AWS credentials with IAM read-only access (iam:GetAccountAuthorizationDetails)
- Optional: cloudsplaining Python package for HTML report generation

## Steps

1. **Download IAM Authorization Details** — Call iam:GetAccountAuthorizationDetails to retrieve all users, groups, roles, and policies
2. **Analyze Policies for Privilege Escalation** — Check each policy for known escalation permission combinations
3. **Identify Wildcard Resource Policies** — Flag policies using Resource: "*" with dangerous actions
4. **Map Principal-to-Policy Relationships** — Build a graph of which principals can access which escalation paths
5. **Score and Prioritize Findings** — Rank findings by severity based on escalation vector type
6. **Generate Report** — Produce structured JSON report with remediation guidance

## Expected Output

- JSON report of privilege escalation findings with severity scores
- List of dangerous permission combinations per principal
- Wildcard resource policy audit results
- Remediation recommendations for each finding
