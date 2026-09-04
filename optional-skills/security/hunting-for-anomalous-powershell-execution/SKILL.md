---
name: hunting-for-anomalous-powershell-execution
description: Hunt for malicious PowerShell activity by analyzing Script
version: '1.0'
author: mahipal (vendored by SOCIS)
license: Apache-2.0
platforms:
- linux
- macos
- windows
category: security
metadata:
  socis:
    tags:
    - powershell
    - script-block-logging
    - event-4104
    - amsi
    - threat-hunting
    - evtx
    - obfuscation
    subdomain: threat-hunting
    upstream: mukul975/Anthropic-Cybersecurity-Skills
    nist_csf:
    - DE.CM-01
    - DE.AE-02
    - DE.AE-07
    - ID.RA-05
    mitre_attack:
    - T1046
    - T1057
    - T1082
    - T1083
    - T1003
---

# Hunting for Anomalous PowerShell Execution

## Overview

PowerShell Script Block Logging (Event ID 4104) records the full deobfuscated script text
executed on a Windows endpoint, making it the primary data source for hunting malicious
PowerShell. Combined with Module Logging (4103) and process creation events, analysts can
detect encoded commands, AMSI bypass patterns, download cradles, credential theft tools,
and fileless attack techniques even when the attacker uses obfuscation layers.


## When to Use

- When investigating security incidents that require hunting for anomalous powershell execution
- When building detection rules or threat hunting queries for this domain
- When SOC analysts need structured procedures for this analysis type
- When validating security monitoring coverage for related attack techniques

## Prerequisites

- Windows Event Log exports (.evtx) from Microsoft-Windows-PowerShell/Operational
- Python 3.8+ with python-evtx and lxml libraries
- Script Block Logging enabled via Group Policy
- Understanding of common PowerShell attack techniques

## Steps

1. Parse EVTX files extracting Event 4104 script block text and metadata
2. Reassemble multi-part script blocks using ScriptBlock ID correlation
3. Scan script text for AMSI bypass indicators and obfuscation patterns
4. Detect encoded command execution and base64 payloads
5. Identify download cradles, credential dumping, and lateral movement commands
6. Score and prioritize findings by threat severity

## Expected Output

```json
{
  "total_events": 1247,
  "suspicious_events": 23,
  "amsi_bypass_attempts": 2,
  "encoded_commands": 8,
  "download_cradles": 5,
  "credential_access": 3
}
```
