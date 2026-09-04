---
title: "Implementing Memory Protection With Dep Aslr — Implements memory protection mechanisms including DEP (Data"
sidebar_label: "Implementing Memory Protection With Dep Aslr"
description: "Implements memory protection mechanisms including DEP (Data"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Implementing Memory Protection With Dep Aslr

Implements memory protection mechanisms including DEP (Data

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `socis skills install official/security/implementing-memory-protection-with-dep-aslr` |
| Path | `optional-skills/security/implementing-memory-protection-with-dep-aslr` |
| Version | `1.0.0` |
| Author | mahipal (vendored by SOCIS) |
| License | Apache-2.0 |
| Platforms | linux, macos, windows |
| Tags | `endpoint`, `memory-protection`, `DEP`, `ASLR`, `exploit-mitigation`, `CFG` |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Implementing Memory Protection with DEP and ASLR

## When to Use

Use this skill when hardening endpoints against memory-based exploits by configuring DEP, ASLR, CFG, and Windows Exploit Protection system-wide and per-application mitigations.

## Prerequisites

- Windows 10/11 or Windows Server 2016+ with administrative privileges
- Group Policy management access for enterprise-wide deployment
- Understanding of memory corruption attack techniques (buffer overflow, ROP chains)
- Test environment for validating application compatibility with exploit mitigations

## Workflow

### Step 1: Configure System-Level Mitigations

```powershell
# Enable system-wide DEP (Data Execution Prevention)
# Boot configuration: OptIn (default), OptOut (recommended), AlwaysOn
bcdedit /set nx AlwaysOn

# Verify ASLR status (enabled by default on modern Windows)
Get-ProcessMitigation -System
# MandatoryASLR, BottomUpASLR, HighEntropyASLR should be ON

# Enable all system-level mitigations
Set-ProcessMitigation -System -Enable DEP,SEHOP,ForceRelocateImages,BottomUp,HighEntropy
```

### Step 2: Configure Per-Application Mitigations

```powershell
# Harden high-risk applications (browsers, Office, PDF readers)
Set-ProcessMitigation -Name "WINWORD.EXE" -Enable DEP,SEHOP,ForceRelocateImages,CFG,StrictHandle
Set-ProcessMitigation -Name "EXCEL.EXE" -Enable DEP,SEHOP,ForceRelocateImages,CFG,StrictHandle
Set-ProcessMitigation -Name "AcroRd32.exe" -Enable DEP,SEHOP,ForceRelocateImages,CFG
Set-ProcessMitigation -Name "chrome.exe" -Enable DEP,CFG,ForceRelocateImages
Set-ProcessMitigation -Name "msedge.exe" -Enable DEP,CFG,ForceRelocateImages

# Export configuration for deployment
Get-ProcessMitigation -RegistryConfigFilePath "C:\exploit_protection.xml"
# Deploy via Intune or GPO
```

### Step 3: Deploy via Intune/GPO

```
Intune: Endpoint Security → Attack Surface Reduction → Exploit Protection
  Import exploit_protection.xml template

GPO: Computer Configuration → Admin Templates → Windows Components
  → Windows Defender Exploit Guard → Exploit Protection
  → "Use a common set of exploit protection settings" → Enabled
  → Point to XML file on network share
```

## Key Concepts

| Term | Definition |
|------|-----------|
| **DEP** | Marks memory pages as non-executable to prevent shellcode execution in data regions |
| **ASLR** | Randomizes memory addresses of loaded modules to defeat hardcoded ROP gadgets |
| **CFG** | Validates indirect call targets at runtime to prevent control flow hijacking |
| **SEHOP** | Validates SEH chain integrity to prevent SEH-based exploitation |

## Tools & Systems
- **Windows Exploit Protection**: Built-in per-process mitigation management
- **EMET (legacy)**: Enhanced Mitigation Experience Toolkit (predecessor, now deprecated)
- **ProcessMitigations PowerShell**: Get/Set-ProcessMitigation cmdlets

## Common Pitfalls
- **DEP compatibility**: Legacy 32-bit applications may crash with DEP AlwaysOn. Use OptOut with exceptions.
- **Mandatory ASLR breaking apps**: Some applications are not ASLR-compatible. Test before enforcing ForceRelocateImages.
- **CFG limited to compiled-in support**: CFG only works for applications compiled with /guard:cf. Cannot be retroactively applied.
