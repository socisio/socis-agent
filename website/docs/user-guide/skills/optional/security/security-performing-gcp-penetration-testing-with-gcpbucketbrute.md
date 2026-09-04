---
title: "Performing Gcp Penetration Testing With Gcpbucketbrute — Performs authorized GCP security testing using"
sidebar_label: "Performing Gcp Penetration Testing With Gcpbucketbrute"
description: "Performs authorized GCP security testing using"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Performing Gcp Penetration Testing With Gcpbucketbrute

Performs authorized GCP security testing using

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/performing-gcp-penetration-testing-with-gcpbucketbrute` |
| Path | `optional-skills/security/performing-gcp-penetration-testing-with-gcpbucketbrute` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `gcp`, `cloud-pentesting`, `bucket-enumeration`, `iam-audit`, `privilege-escalation`, `gcpbucketbrute` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Performing GCP Penetration Testing with GCPBucketBrute

## Overview

This skill covers Google Cloud Platform security testing using GCPBucketBrute for storage bucket enumeration and access permission testing, combined with gcloud CLI IAM enumeration to identify privilege escalation paths. The approach tests for publicly accessible buckets, overly permissive IAM bindings, and service account key exposure.


## When to Use

- When conducting security assessments that involve performing gcp penetration testing with gcpbucketbrute
- When following incident response procedures for related security events
- When performing scheduled security testing or auditing activities
- When validating security controls through hands-on testing

## Prerequisites

- Python 3.8+ with google-cloud-storage library
- GCPBucketBrute installed from RhinoSecurityLabs GitHub
- gcloud CLI authenticated with test credentials
- Authorized penetration testing scope for target GCP project
- google-api-python-client and google-auth libraries

## Steps

1. **Enumerate Storage Buckets** — Use GCPBucketBrute with keyword permutations to discover accessible GCP storage buckets
2. **Test Bucket Permissions** — Call TestIamPermissions API on each discovered bucket to determine read/write/admin access levels
3. **Audit IAM Bindings** — Enumerate project-level IAM policies to identify overly permissive role bindings
4. **Check Service Account Keys** — Identify service accounts with user-managed keys and test for privilege escalation via impersonation
5. **Test Privilege Escalation Paths** — Check for iam.serviceAccounts.actAs, setIamPolicy, and other privilege escalation vectors
6. **Generate Findings Report** — Produce a structured security assessment with risk severity ratings

## Expected Output

- JSON report of discovered buckets with permission levels
- IAM privilege escalation path analysis
- Service account security assessment
- Risk-scored findings with remediation recommendations
