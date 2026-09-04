---
title: "Analyzing Kubernetes Audit Logs — Parses Kubernetes API server audit logs (JSON lines) to"
sidebar_label: "Analyzing Kubernetes Audit Logs"
description: "Parses Kubernetes API server audit logs (JSON lines) to"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Analyzing Kubernetes Audit Logs

Parses Kubernetes API server audit logs (JSON lines) to

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/analyzing-kubernetes-audit-logs` |
| Path | `optional-skills/security/analyzing-kubernetes-audit-logs` |
| Version | `1.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `kubernetes-security`, `container-security`, `audit-log-analysis`, `rbac`, `privilege-escalation`, `k8s-api-server`, `threat-detection` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Analyzing Kubernetes Audit Logs


## When to Use

- When investigating security incidents that require analyzing kubernetes audit logs
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Familiarity with container security concepts and tools
- Access to a test or lab environment for safe execution
- Python 3.8+ with required dependencies installed
- Appropriate authorization for any testing activities

## Instructions

Parse Kubernetes audit log files (JSON lines format) to detect security-relevant
events including unauthorized access, privilege escalation, and data exfiltration.

```python
import json

with open("/var/log/kubernetes/audit.log") as f:
    for line in f:
        event = json.loads(line)
        verb = event.get("verb")
        resource = event.get("objectRef", {}).get("resource")
        user = event.get("user", {}).get("username")
        if verb == "create" and resource == "pods/exec":
            print(f"Pod exec by {user}")
```

Key events to detect:
1. pods/exec and pods/attach (shell into containers)
2. secrets access (get/list/watch)
3. clusterrolebindings creation (RBAC escalation)
4. Privileged pod creation
5. Anonymous or system:unauthenticated access

## Examples

```python
# Detect secret enumeration
if verb in ("get", "list") and resource == "secrets":
    print(f"Secret access: {user} -> {event['objectRef'].get('name')}")
```
