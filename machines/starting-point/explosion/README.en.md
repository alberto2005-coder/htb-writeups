---
machine: Explosion
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [windows, rdp, blank-password, misconfiguration]
---

# Explosion — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available (Starting Point), publishable.
> Reference notes. No real flags or credentials.

## TL;DR

A Windows host with **RDP open and the `Administrator` account passwordless**. There is no exploit: connect over Remote Desktop, accept the certificate and log in with the password field left empty. The flag sits on the administrator's desktop.

## Recon

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
135/tcp   msrpc        Microsoft Windows RPC
139/tcp   netbios-ssn
445/tcp   microsoft-ds
3389/tcp  ms-wbt-server  Microsoft Terminal Services
```

Three SMB/RPC ports plus Remote Desktop on 3389. SMB can be listed anonymously, but it is not needed: 3389 is the door.

## Access

```bash
xfreerdp /v:<IP> /cert:ignore /u:Administrator
```

At the credential prompt press **Enter with nothing typed**: the account has no password and policy allows the logon.

```bash
# alternative
rdesktop <IP> -u Administrator -p ""
```

Once on the desktop:

```text
C:\Users\Administrator\Desktop\flag.txt
```

## Evidence (redacted)

```text
C:\Users\Administrator\Desktop\flag.txt  -> <flag>
```

## Lessons

- A blank-password account with RDP exposed is full access with no exploit; Windows allows it by default on machines outside a domain.
- Mitigation: `LimitBlankPasswordUse = 1`, require NLA (`UserAuthentication = 1`), set local passwords, and keep RDP behind VPN or a jump host.
- Detection: event 4624 type 10 from unusual addresses and repeated 4625 for `Administrator`.
