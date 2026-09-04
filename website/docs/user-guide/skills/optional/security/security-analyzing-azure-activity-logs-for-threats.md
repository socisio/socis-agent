---
title: "Analyzing Azure Activity Logs For Threats — Queries Azure Monitor activity logs and sign-in logs via"
sidebar_label: "Analyzing Azure Activity Logs For Threats"
description: "Queries Azure Monitor activity logs and sign-in logs via"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Analyzing Azure Activity Logs For Threats

Queries Azure Monitor activity logs and sign-in logs via

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/analyzing-azure-activity-logs-for-threats` |
| Path | `optional-skills/security/analyzing-azure-activity-logs-for-threats` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `azure`, `cloud-security`, `azure-monitor`, `kql`, `threat-hunting`, `activity-logs` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Analyzing Azure Activity Logs for Threats


## When to Use

- When investigating security incidents that require analyzing azure activity logs for threats
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with security operations concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Use azure-monitor-query to execute KQL queries against Azure Log Analytics workspaces,
detecting suspicious admin operations and sign-in anomalies.

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from datetime import timedelta

credential = DefaultAzureCredential()
client = LogsQueryClient(credential)

response = client.query_workspace(
    workspace_id="WORKSPACE_ID",
    query="AzureActivity | where OperationNameValue has 'MICROSOFT.AUTHORIZATION/ROLEASSIGNMENTS/WRITE' | take 10",
    timespan=timedelta(hours=24),
)
```

Key detection queries:
1. Role assignment changes (privilege escalation)
2. Resource group and subscription modifications
3. Key vault secret access from new IPs
4. Network security group rule changes
5. Conditional access policy modifications

## Examples

```python
# Detect new Global Admin role assignments
query = '''
AuditLogs
| where OperationName == "Add member to role"
| where TargetResources[0].modifiedProperties[0].newValue has "Global Administrator"
'''
```
