---
title: "Detecting Malicious Scheduled Tasks With Sysmon — Detect malicious scheduled task creation and modification"
sidebar_label: "Detecting Malicious Scheduled Tasks With Sysmon"
description: "Detect malicious scheduled task creation and modification"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Detecting Malicious Scheduled Tasks With Sysmon

Detect malicious scheduled task creation and modification

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/detecting-malicious-scheduled-tasks-with-sysmon` |
| Path | `optional-skills/security/detecting-malicious-scheduled-tasks-with-sysmon` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `sysmon`, `scheduled-tasks`, `persistence`, `detection`, `threat-hunting`, `windows-security` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Detecting Malicious Scheduled Tasks with Sysmon

## Overview

Adversaries abuse Windows Task Scheduler (schtasks.exe, at.exe) for persistence (T1053.005)
and lateral movement. Sysmon Event ID 1 captures schtasks.exe process creation with full
command-line arguments, while Event ID 11 captures task XML files written to
C:\Windows\System32\Tasks\. Windows Security Event 4698 logs task registration details.
This skill covers building detection rules that correlate these events to identify
malicious scheduled tasks created from suspicious paths, with encoded payloads, or
targeting remote systems.


## When to Use

- When investigating security incidents that require detecting malicious scheduled tasks with sysmon
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Sysmon installed with a detection-focused configuration (e.g., SwiftOnSecurity or Olaf Hartong)
- Windows Event Log forwarding to SIEM (Splunk, Elastic, or Sentinel)
- PowerShell ScriptBlock Logging enabled (Event 4104)

## Steps

1. Configure Sysmon to log Event IDs 1, 11, 12, 13 with task-related filters
2. Build detection rules for schtasks.exe /create with suspicious arguments
3. Correlate Event 4698 (task registered) with Sysmon Event 1 (process create)
4. Hunt for tasks executing from public directories or with encoded commands
5. Alert on remote task creation (schtasks /s) for lateral movement detection

## Expected Output

```
[CRITICAL] Suspicious Scheduled Task Detected
  Task: \Microsoft\Windows\UpdateCheck
  Command: powershell.exe -enc SQBuAHYAbwBrAGUALQBXAGUAYgBSAGU...
  Created By: DOMAIN\compromised_user
  Parent Process: cmd.exe (PID 4532)
  Source: \\192.168.1.50 (remote creation)
  MITRE: T1053.005 - Scheduled Task/Job
```
