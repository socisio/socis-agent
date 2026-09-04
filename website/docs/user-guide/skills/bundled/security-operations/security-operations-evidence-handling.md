---
title: "Evidence Handling — Acquire and preserve digital evidence (ISO 27037)"
sidebar_label: "Evidence Handling"
description: "Acquire and preserve digital evidence (ISO 27037)"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Evidence Handling

Acquire and preserve digital evidence (ISO 27037).

## Skill metadata

| | |
|---|---|
| Source | Bundled (installed by default) |
| Path | `skills/security-operations/evidence-handling` |
| Version | `1.0.0` |
| Author | SOCIS |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `Security`, `DFIR`, `Forensics`, `ChainOfCustody` |
| Related skills | [`incident-response`](/docs/user-guide/skills/bundled/security-operations/security-operations-incident-response), [`alert-triage`](/docs/user-guide/skills/bundled/security-operations/security-operations-alert-triage) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that SOCIS loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Evidence Handling

Acquiring and preserving digital evidence so it survives scrutiny — from a
customer's auditor, their insurer, opposing counsel, or a court.

Grounded in **ISO/IEC 27037** (identification, collection, acquisition,
preservation) and **RFC 3227** (order of volatility, minimum custody record).

---

## Read this first

**You are almost certainly not the customer's lawyer.** This skill produces
technically defensible evidence handling. Whether evidence is *admissible* is a
legal determination that varies by jurisdiction, and it is not yours to make.

When work may touch litigation, regulatory notification, insurance claims, or
law enforcement:

- Say so early and get the customer's counsel involved
- Do not advise on legal sufficiency
- Do not destroy or alter anything, including "cleaning up" during response
- Assume every action you take will be reviewed line by line

Three failure modes that destroy evidentiary value, in order of frequency:

1. **Acting before documenting** — no contemporaneous record of what you did
2. **Breaking the chain** — an unexplained gap in custody
3. **Working on the original** — analysis on the source rather than a verified copy

---

## Order of volatility (RFC 3227)

Collect most-volatile first. Anything below the line you cross is still there;
anything above it is gone forever.

| # | Source | Lost when |
|---|---|---|
| 1 | CPU registers, cache | microseconds — practically uncollectable |
| 2 | Routing table, ARP cache, process table, kernel stats | network change / reboot |
| 3 | **RAM** | power off |
| 4 | Temporary filesystems | reboot |
| 5 | Disk | wipe / overwrite |
| 6 | Remote logging, monitoring data | retention expiry |
| 7 | Physical configuration, topology | rebuild |
| 8 | Archival media | — |

**The containment conflict.** Isolating a host preserves volatile state;
pulling power destroys RAM — including in-memory keys, injected code, and
network state that may be the only evidence of what happened. Ransomware makes
this acute: the decryption key may exist only in RAM.

Standard resolution: a **5–10 minute triage collection** capturing the highest
volatility tiers, *then* network isolation. Never power off first.

**Cloud and containers invert some of this.** An ephemeral container's disk is
as volatile as RAM. Snapshot the volume and capture the orchestrator's state
before the workload is rescheduled — a terminated pod takes its filesystem
with it.

---

## Chain of custody

RFC 3227's minimum record for live acquisition:

- **System clock offset** — the difference between the host clock and a trusted
  reference. Without this, your timeline is unanchored.
- **Every command issued**, verbatim
- **Collector identity**
- **Cryptographic hash of each acquired item**

Log form — one row per transfer, no gaps:

```markdown
# Chain of Custody — <case ID>

**Case:** <ID>   **Customer:** <name>   **Opened:** <UTC>
**Incident:** <one line>

## Item CoC-001
| Field | Value |
|---|---|
| Description | Memory image, WIN-DC01 |
| Source host | WIN-DC01 (10.4.2.11), Windows Server 2022 |
| Acquired by | <name, role, organisation> |
| Acquired at | 2026-09-04T14:22:00Z |
| Host clock offset | +00:00:03 vs pool.ntp.org (verified pre-acquisition) |
| Method | winpmem v4.0.1 |
| Exact command | `winpmem.exe --format raw -o E:\WIN-DC01-mem.raw` |
| Size | 34,359,738,368 bytes |
| SHA-256 | a3f5...9c2e |
| Hash computed | at acquisition, on the acquiring host |
| Storage | Evidence-01, encrypted volume, `/cases/<ID>/` |

### Custody transfers
| # | From | To | UTC | Purpose | Hash re-verified |
|---|---|---|---|---|---|
| 1 | <analyst> | Evidence-01 | ...T14:40:00Z | Storage | Yes — matches |
| 2 | Evidence-01 | <examiner> | ...T09:12:00Z | Analysis | Yes — matches |
```

**Rules that make or break the record:**

- **Hash at the moment of acquisition**, before the item moves anywhere.
- **Re-verify at every transfer.** A hash checked only at the start proves
  nothing about what happened in between.
- **Never a gap.** Every minute between acquisition and analysis is accounted
  for by either a custody entry or documented sealed storage.
- **Contemporaneous notes.** Written *during* the work. Notes reconstructed
  days later are materially weaker and will be challenged as such.
- **SHA-256 or better.** MD5 and SHA-1 have practical collisions and invite an
  easy challenge.
- **Record failures too.** A tool that crashed, a command that errored, a
  partial acquisition — omitting these looks like concealment.

---

## Acquisition

### Memory

```bash
# Linux
sudo ./avml /evidence/<host>-mem.lime
sudo insmod lime.ko "path=/evidence/<host>-mem.lime format=lime"

# Windows
winpmem.exe --format raw -o E:\<host>-mem.raw
DumpIt.exe /OUTPUT E:\<host>-mem.raw

# macOS — SIP generally blocks this; document the constraint rather than
# disabling SIP, which is itself an alteration of the system.
```

Write to **external or network storage**, never the host's own disk — that
overwrites unallocated space that may hold evidence.

### Disk

```bash
# Write blocker on the source. Always, for physical media.
sudo dc3dd if=/dev/sdb of=/evidence/<host>-disk.dd hash=sha256 log=/evidence/<host>.log

# E01 with metadata and compression
sudo ewfacquire -t /evidence/<host>-disk -d sha256 /dev/sdb
```

### Cloud

```bash
aws ec2 create-snapshot --volume-id vol-xxxx --description "IR case <ID>"
az snapshot create -g <rg> -n <case>-snap --source <disk-id>
gcloud compute disks snapshot <disk> --snapshot-names=<case>-snap
```

Also capture, before anything is rebuilt: instance metadata, IAM role and
policy, security groups, VPC flow logs, and the control-plane audit trail
(CloudTrail / Azure Activity / GCP Audit Logs). The control-plane record is
frequently the only evidence of how access was obtained.

### Verify — every time

```bash
sha256sum /evidence/<host>-mem.raw | tee /evidence/<host>-mem.raw.sha256
```

Then re-verify **before** analysis begins and record the result. Work only on a
copy; the original goes to sealed storage untouched.

---

## Multi-tenant discipline

Running IR as a service across customers adds obligations a single-org team
does not have:

- **Physical and logical separation.** One customer's evidence never shares a
  volume, working directory, or analysis VM with another's.
- **Case ID on everything.** Every path, artifact, and note.
- **Scoped access.** Only assigned examiners; log every access.
- **Retention per contract.** Different customers have different obligations —
  and deleting evidence still under legal hold is a serious problem. Confirm
  hold status before any disposal.
- **Data residency.** Moving a customer's evidence across a border can breach
  GDPR or local law. Check before transfer, not after.

---

## Pitfalls

- Powering off before capturing RAM
- Analysing the original instead of a verified copy
- MD5-only hashing
- Writing acquisitions to the subject host's own disk
- Notes written after the fact
- Undocumented gaps in custody
- Skipping the clock offset — timelines then cannot be reconciled
- Omitting failed attempts
- Deleting anything during response "to clean up"

---

## Verification

- [ ] Volatility order respected; rationale recorded for any deviation
- [ ] Clock offset captured against a trusted reference
- [ ] SHA-256 computed at acquisition and re-verified at each transfer
- [ ] Every command recorded verbatim, including failures
- [ ] Custody log has no unexplained gaps
- [ ] Originals sealed; analysis performed on copies
- [ ] Evidence isolated to a single customer's case
- [ ] Legal hold and residency constraints confirmed
- [ ] Counsel engaged where litigation or notification is plausible
