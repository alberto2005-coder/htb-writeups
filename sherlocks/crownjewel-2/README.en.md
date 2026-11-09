---
title: CrownJewel-2
category: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, pass-the-hash, smb, evtx]
---

# CrownJewel-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

## Scenario

A follow-up to CrownJewel-1: the attacker already owns an account and moves across the domain. Evidence is event logs from the DCs and the compromised host; the task is to reconstruct lateral movement and tell it apart from legitimate admin traffic.

## Evidence and setup

```bash
unzip crownjewel2.zip        # usual password: hacktheblue
sha256sum *                  # inventory before touching anything
EvtxECmd.exe -d Logs --csv out --csvf all.csv
```

Useful channels: `Security.evtx`, `System.evtx`, `Microsoft-Windows-Sysmon/Operational`, `PowerShell/Operational` and the SMB service log.

## Questions the analysis answers

1. Which account authenticated first after the compromise?
2. Which hosts received that logon, and in what order?
3. Was a hash used instead of a password?
4. Which resource was read or copied?

## Method

- Filter **4624 type 3** and **type 10**, grouped by `TargetUserName`, `IpAddress` and time. The same user appearing on hosts they never work on is the signal.
- **4624 with NTLM `AuthenticationPackage`** and empty/`NtLmSsp` `LogonProcess` points to *pass-the-hash*; Kerberos would show `Kerberos` and a prior TGT.
- Cross-check **5140/5145** for the share accessed and **4662** for AD objects.
- DC **4768/4769** give context: no TGT for that account before the 4624 means the logon used a hash or cleartext credential.
- Build a timeline (`Timeline Explorer`) and keep the first occurrence of each user/host pair.

## Findings (pattern)

```text
4624 type 3  user=<account>  src=<attacker host>  auth=NTLM
5145         share=\\ <host>\C$  access=ReadData
4662         object=DC=<domain>  DS-Replication-Get-Changes
```

NTLM + `C$` access + AD reads without a prior TGT describe the movement and the goal; that is not a normal interactive logon.

## Lessons

- Pass-the-hash produces no 4768: the absence of Kerberos is as informative as a 4624.
- Baseline the user to avoid false positives from admin tooling.
- Administrative shares (`C$`, `ADMIN$`) are the best lateral-movement indicator.

## Detection and mitigation

- Alert on 4624 type 3 with NTLM from non-admin hosts.
- Protect privileged accounts (LAPS, `Protected Users`, restricted credentials).
- Segment and restrict `C$`/`ADMIN$`; audit 5140/5145.
- Rotate the compromised hash and review active sessions.

MITRE: T1550.002, T1021.002, T1078.
