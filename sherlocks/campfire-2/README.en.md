---
title: Campfire-2
category: DFIR / Active Directory
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, asrep, kerberos, evtx]
---

# Campfire-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

## Scenario

Part two of Campfire: after the ticket theft in the first scenario, the attacker obtains an account and hunts for more credentials. Evidence is again a set of event logs from a small domain; the focus is **AS-REP roasting** and later use of the account.

## Evidence and setup

```bash
EvtxECmd.exe -d . --csv out --csvf evtx.csv
```

Channels: `Security.evtx`, `System.evtx` and `Microsoft-Windows-PowerShell/Operational`.

## Method

- **4768** with `PreAuthType = 0` (no pre-authentication) is the AS-REP signature: the DC returns a blob encrypted with the user's password.
- Group 4768 by `TargetUserName` and time; an account receiving many in seconds is being enumerated or roasted.
- Then look for **4624 type 3/10** of that account on hosts it does not usually touch, and **4769** for the services requested.
- In PowerShell, **4104** may hold the command that generated the ticket (Rubeus, `GetNPUsers`, `Invoke-Kerberoast`).
- Cross-check the KDC service log when present: `TicketOptions` and `Status` separate success from failure.

## Findings (pattern)

```text
4768  user=<account>  PreAuthType=0  Status=0x0
4624  type=3  user=<account>  src=<attacker host>
4769  service=<SPN>  enc=0x17
```

The sequence 4768 without preauth → 4624 on a new host → 4769 RC4 describes credential theft and its use.

## Lessons

- AS-REP needs no authentication: any user can trigger it and the DC logs it the same way.
- An account without pre-authentication is a configuration weakness, not a password failure.
- RC4 encryption in 4769 remains the most reliable Kerberoasting indicator.

## Detection and mitigation

- Alert on 4768 with `PreAuthType=0` outside business hours or in volume.
- Enable pre-authentication on every account and use long passwords for service accounts.
- Enforce AES and review unnecessary SPNs.
- Audit 4104 for Rubeus/`GetNPUsers` signatures.

MITRE: T1558.004, T1558.003, T1078.
