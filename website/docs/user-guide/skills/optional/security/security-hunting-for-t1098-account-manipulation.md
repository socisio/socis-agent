---
title: "Hunting For T1098 Account Manipulation — Hunts for MITRE ATT&CK T1098 account manipulation - shadow"
sidebar_label: "Hunting For T1098 Account Manipulation"
description: "Hunts for MITRE ATT&CK T1098 account manipulation - shadow"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Hunting For T1098 Account Manipulation

Hunts for MITRE ATT&CK T1098 account manipulation - shadow

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/hunting-for-t1098-account-manipulation` |
| Path | `optional-skills/security/hunting-for-t1098-account-manipulation` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `threat-hunting`, `mitre-attack`, `t1098`, `account-manipulation`, `active-directory`, `persistence` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Hunting for T1098 Account Manipulation

## Overview

MITRE ATT&CK T1098 (Account Manipulation) covers adversary actions to maintain or expand access to compromised accounts, including adding credentials, modifying group memberships, SID history injection, and creating shadow admin accounts. This skill covers detecting these techniques through Windows Security Event Log analysis (Event IDs 4738, 4728, 4732, 4756, 4670, 5136), correlating group membership changes with privilege escalation indicators, and identifying anomalous account modification patterns.


## When to Use

- When investigating security incidents that require hunting for t1098 account manipulation
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Windows Security Event Logs (EVTX format) or SIEM access
- Python 3.9+ with `python-evtx`, `lxml` libraries
- Understanding of Active Directory group structure and SID architecture
- Familiarity with MITRE ATT&CK T1098 sub-techniques

## Steps

### Step 1: Parse Account Modification Events
Extract Event IDs 4738 (user account changed), 4728/4732/4756 (member added to security groups), and 5136 (directory service object modified).

### Step 2: Detect Privileged Group Changes
Flag additions to Domain Admins, Enterprise Admins, Schema Admins, Administrators, and Backup Operators groups.

### Step 3: Identify Shadow Admin Indicators
Detect accounts receiving AdminSDHolder protection, direct privilege assignment, or SID history injection.

### Step 4: Correlate with Attack Timeline
Cross-reference account changes with authentication events to identify initial compromise and persistence establishment.

## Expected Output

JSON report with detected account manipulation events, privileged group changes, shadow admin indicators, and timeline correlation.
