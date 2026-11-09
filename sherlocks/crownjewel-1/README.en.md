---
sherlock: CrownJewel-1
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, ntds, vss, credential-dumping, mft]
---

# CrownJewel-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

Forela suspects its Active Directory has been compromised. The response team provides an image of the domain controller and artefacts from the affected hosts. The goal is to reconstruct what the intruder did, how domain credentials were obtained, and which evidence proves it.

## Evidence

- The DC volume `$MFT`, with both `$SI` and `$FN` timestamps.
- `NTFS.evtx` (file system record) plus `SECURITY.evtx` / `SYSTEM.evtx`.
- A copy of the `NTDS` folder and the `SYSTEM` hive, if the attacker extracted them.

## Investigation

### 1. Creating a shadow copy

The first lead is the execution of volume snapshot utilities on the DC:

```powershell
vssadmin create shadow /for=C:
# or equivalent alternatives
diskshadow.exe
wmic shadowcopy call create Volume='C:\'
```

`SECURITY.evtx`/`SYSTEM.evtx` show the `VSS` service (`vssvc.exe`) and, when process auditing is on, a `4688` with `vssadmin.exe` or `diskshadow.exe` in the command line.

### 2. Extracting NTDS.dit

From the shadow copy the attacker reaches `C:\Windows\NTDS\ntds.dit`, the directory database, and copies it together with the `SYSTEM` hive (needed for the boot key). The `$MFT` pins down creation and copy times: compare `$SI` (content changes) with `$FN` (name metadata) to spot timestomping.

```bash
# parsing the $MFT with the case tooling
MFTECmd.exe -f '$MFT' --csv out/
```

### 3. What was taken

`ntds.dit` plus `SYSTEM` lets an attacker dump every domain hash with `secretsdump`/`impacket` and obtain `krbtgt`, enabling golden-ticket persistence. The key evidence is the **copy** of both files, not a `4662` replication event: this was file theft, not DCSync.

## Findings

- Domain control was obtained by copying `NTDS.dit` and the `SYSTEM` hive from a volume snapshot created with `vssadmin`/`diskshadow`, not through directory replication.
- With `krbtgt` in the attacker's hands, a double password reset is mandatory even if no golden ticket appears in the logs.
- Scope is the whole domain: every account and host is compromised.

## Lessons

- Creating a shadow copy on a DC is a recon/exfiltration step, not routine administration: `vssadmin` and `diskshadow` must alert.
- `ntds.dit` + `SYSTEM` is equivalent to DCSync: impact is measured by the file, not only by event `4662`.
- The `$MFT` proves the copy and defeats timestomping by comparing `$SI` with `$FN`.
- Response starts by isolating the DC, resetting `krbtgt` twice, and reviewing privileged accounts.

## References

- [MITRE T1003.003 — OS Credential Dumping: NTDS](https://attack.mitre.org/techniques/T1003/003/)
- [Microsoft Learn — vssadmin](https://learn.microsoft.com/windows-server/administration/windows-commands/vssadmin)
