---
sherlock: Jinkies
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: KAPE triage (TriageData + LiveResponse) of a workstation with IP theft
tools: [EvtxECmd, MFTECmd, Chainsaw, Registry Explorer, secretsdump]
state: Active
tags: [dfir, windows, kape, smb, credential-reuse, exfiltration, t1021.002]
---

# Jinkies — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Active. Investigation notes; no platform answers.

## Scenario

Cloud-Guru investigates the leak of a proprietary design. The suspect is an employee with legitimate access to an engineering share. A KAPE triage of the workstation is provided, with live data and a filesystem copy.

## Evidence

- `TriageData/`: EVTX, `$MFT`, hives and the Chrome profile.
- `LiveResponse/`: processes, ports, CrowdResponse output and `config.7z` with SAM/SYSTEM.
- About 3,104 files in total.

```bash
sha256sum -c hashes.txt 2>/dev/null; ls TriageData LiveResponse
```

## Investigation

### 1. Inventory and triage

Volume forces choices: `$MFT` for objects, Security for logons, Sysmon for execution. Chainsaw filters without opening 3,000 files one by one:

```bash
chainsaw hunt TriageData -s sigma/rules --mapping mappings/sigma-event-logs-all.yml \
  --csv out --output chainsaw.csv
EvtxECmd.exe -d TriageData/Windows/System32/winevt/Logs --csv out --csvf evtx.csv
```

### 2. Timeline

Security shows a **4624 Logon Type 3** (network) for `Velma` from `192.168.157.151` at **17:15:56**: access to a share from another internal machine, not an interactive logon.

Two minutes later Sysmon **EID 1** records `cmd.exe` at **17:17:43** and, in the same session, `net group` and `net users`: account and group enumeration after getting in.

The share lives in the registry:

```text
HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares
```

There sits the legitimate engineering resource and its path.

### 3. Key artifact

In `Documents` there is a `bk_db.ibd` (a MySQL database copy) with clear-text credentials: no cracking needed, just open the file. The `config.7z` hives confirm the reuse:

```bash
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

The local NTLM hash matches the password found in the backup: the same key was used for the database and the local account.

`$MFT` closes the case: `learn.txt` was **created by the attacker** in their profile, not by the employee, and holds the password used for access. Creation, not modification, is what proves authorship.

## Findings

- SMB access with valid `Velma` credentials from an internal machine, followed by `net group`/`net users` enumeration.
- The password came from a clear-text database backup in the suspect's profile and was reused on the local account.
- IP theft through local copying; the attacker-created `learn.txt` is the authorship evidence.

## Lessons

- A `Logon Type 3` with a specific username rules out anonymous access: there is a credential, and it must be found.
- Database backups (`*.ibd`, `.sql`, `.bak`) are almost never encrypted and hold credentials.
- Password reuse turns a backup leak into host access.
- `$MFT` separates creation from modification; for authorship, creation time rules.

## Mitigations and detection

- Encrypt database backups and keep them out of user profiles.
- Unique per-service passwords; corporate vault and post-incident rotation.
- Monitor 5140/5145 access to sensitive shares and the enumeration that follows (`net group`, `net users` → Sysmon 1 with those command lines).
- Retain Sysmon and Security long enough to rebuild two minutes of activity.

MITRE: T1021.002 (SMB/admin shares), T1087.002 (domain account discovery), T1552.001 (credentials in files), T1005 (data from local system), T1078 (valid accounts).

## References

- <https://mwalkowski.com/post/sherlock-jinkies>
- <https://inksec.io/blue-team/sherlocks/jinkies>
- <https://github.com/WithSecureLabs/chainsaw>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-5140>
