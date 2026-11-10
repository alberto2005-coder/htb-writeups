---
topic: smb-enumeration
tags: [smb, windows, enumeration, null-session]
---

# SMB enumeration — null sessions, shares and credentials

**English** | [🇪🇸 Español](smb-enumeration.md)

> Reusable note. Do not publish output containing real credentials.

## Idea

SMB (139/445) is the most talkative service on Windows: host and domain names, shares, users, policies and sometimes configuration files with passwords. The **null session** (empty user) and **guest** are the first two attempts; if they fail, try credentials you already hold.

## Ports and services

| Port | Service | Use |
|---|---|---|
| 139/tcp | NetBIOS session | SMB over NetBIOS (legacy) |
| 445/tcp | SMB direct | File sharing and IPC |
| 135/tcp | MSRPC | `rpcclient`, user enumeration |
| 389/636 | LDAP | AD enumeration when a domain exists |

## Unauthenticated enumeration

```bash
nmap -Pn -p 139,445 --script "smb-os-discovery,smb-enum-shares,smb-enum-users,smb2-security-mode" <IP>
smbclient -L //<IP> -N
smbclient //<IP>/<SHARE> -N
rpcclient -U '' -N <IP> -c 'enumdomusers'
nxc smb <IP> -u '' -p '' --shares
```

What to look for:

- **Non-admin shares** (`backups`, `data`, `www`, `IT`): usually hold configuration, backups and scripts.
- **Write permissions**: a writable share lets you drop a file another user will execute.
- **Null session enabled**: confirms a lax policy and opens `IPC$` for enumeration.
- **SMB signing disabled**: enables NTLM relay.

## With credentials

```bash
nxc smb <IP> -u <USER> -p '<PASS>' --shares --sessions --loggedon-users
smbclient //<IP>/<SHARE> -U '<DOMAIN>\<USER>%<PASS>'
smbmap -H <IP> -u <USER> -p '<PASS>' -R
```

If the account is a local administrator, `nxc` flags it (`Pwn3d!`) and you can execute with `psexec`, `wmiexec` or `smbexec`.

## What to read first in a share

| File | Contents |
|---|---|
| `*.config`, `*.dtsConfig`, `web.config` | connection strings and passwords |
| `*.ps1`, `*.bat`, `*.vbs` | embedded credentials and internal paths |
| `*.kdbx`, `*.psafe3` | password databases (KeePass, Password Safe) |
| `unattend.xml`, `sysprep.inf` | administrator password in clear or base64 |
| `*.bak`, `*.zip`, `*.7z` | database and source-code copies |
| `id_rsa`, `*.pem`, `*.pfx` | private keys and certificates |

## Attacks that follow

- **Password spraying** with the discovered policy (`nxc smb` against a user list).
- **NTLM relay** when signing is disabled (`ntlmrelayx`).
- **Coercion** (`PetitPotam`, `PrinterBug`) to make the host authenticate to you.
- **Pass-the-hash** with the NTLM hash obtained.

## Hardening

- Disable SMBv1 and require **SMB signing** and encryption.
- `RestrictAnonymous=1` and `EveryoneIncludesAnonymous=0`; remove guest access.
- Shares with group-based permissions, no write for `Everyone`.
- Rotated service passwords and no secrets in configuration files.
- Segment 445/139 to the management network.

## Detection

- Event 4624 type 3 with `ANONYMOUS LOGON` or `Administrator` from non-admin workstations.
- Mass share or user enumeration (`rpcclient`, `enum4linux`) in a short window.
- Access to `ADMIN$`/`C$` followed by service creation (7045).
- Outbound SMB connections from servers that should not start them.

## References

- <https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security>
- <https://book.hacktricks.xyz/network-services-pentesting/pentesting-smb>
- <https://attack.mitre.org/techniques/T1021/002/>
