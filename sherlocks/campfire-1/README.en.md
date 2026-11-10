---
sherlock: Campfire-1
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, windows-events, kerberoasting]
---

# Campfire-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

Domain logs after an incident: the company suspects Kerberos abuse. Security events and domain controller logs are provided; the job is to identify the compromised user, the technique and the workstation involved.

## Evidence

- `Security.evtx` and DC service logs.
- Kerberos-related event export (4768, 4769, 4771).
- Host and service-account inventory.

## Investigation

### 1. Look for the Kerberoasting pattern

A `4769` with **RC4 (0x17)** for a service SPN, requested by an unrelated user, is the signature:

```bash
EvtxECmd.exe -f Security.evtx --csv out/
grep "4769" out/*.csv | grep "0x17" | head -20
```

Group by requesting account and `Service Name` to tell a one-off from full enumeration.

### 2. From event to host

The account name and the event's `IpAddress` locate the workstation. Cross it with `4624` (type 3/10) and the preceding interactive logon, usually the real entry point.

### 3. What left

`4769` records show which services were requested; they do not show whether a hash was cracked. The proof is later use of the account: logons from new hosts, type 3 `4624` towards file or mail servers.

## Findings

- Kerberoasting from a specific workstation against service accounts.
- Impact depends on service-password strength, not ticket count.
- The entry point is a compromised standard user, not the DC.

## Lessons

- `4769` with RC4 and an SPN is the event to read from memory.
- Rotating service passwords to 25+ characters or using gMSA kills the technique.
- Without endpoint telemetry the DC says "what" but not "from which process".
