---
machine: Nest
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, encrypted-config, vb-net, alternate-data-stream, hqk, psexec]
---

# Nest — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous SMB exposes a welcome note with `TempUser` credentials. That account reaches `Secure$` and an XML file with `c.smith`'s encrypted password; the scanner's own Visual Basic project contains the decryption routine. `c.smith` reads the user flag and finds a debug password in an NTFS alternate data stream. The HQK service leaks the administrator's encrypted password, and `HqkLdap.exe` decrypts it; `psexec` yields SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p445,4386 <IP>
```

- SMB on 445.
- Custom `HQK Reporting Service V1.2` on 4386.
- Port 4386 answers `HELP`, `LIST`, `SETDIR`, `RUNQUERY` and `DEBUG`.

## Enumeration

```bash
smbclient -N -L //<IP>/
smbclient -N //<IP>/Data
smbclient -N //<IP>/Users
```

`Data` contains `Welcome Email.txt` with `TempUser` / `<TEMP_PASSWORD>`. `Users` lists names but does not allow reading their folders.

With `TempUser`, `Secure$` is readable and IT configs can be downloaded:

```bash
smbclient -U 'TempUser%<TEMP_PASSWORD>' //<IP>/Secure$
recurse on
prompt off
mget *
```

`IT/Configs/RU Scanner/RU_config.xml` contains user `c.smith` and an encrypted password `<CIPHER>`. The `RUScanner` project includes `Utils.vb` with `DecryptString`; running it yields `<CSMITH_PASSWORD>`.

## Foothold

```bash
smbclient -U 'c.smith%<CSMITH_PASSWORD>' //<IP>/Users
```

Read `C.Smith/user.txt` and download `HQK Reporting`. `Debug Mode Password.txt` looks empty, but `allinfo` shows an alternate stream `:Password:$DATA`.

```bash
allinfo "Debug Mode Password.txt"
get "Debug Mode Password.txt:Password"
```

The content is the debug password `<DEBUG_PASSWORD>`.

## Privilege escalation

Connect to the HQK service and enable debug mode:

```bash
telnet <IP> 4386
DEBUG <DEBUG_PASSWORD>
SHOWQUERY 2
```

The query embeds `ldap.conf` with user `Administrator` and another encrypted password. `HqkLdap.exe` is the module that decrypts it; run it with the file as an argument and a breakpoint after the decryption call to read `<ADMIN_PASSWORD>`.

```bash
psexec.py administrator:'<ADMIN_PASSWORD>'@<IP>
```

The shell is `NT AUTHORITY\SYSTEM`; read `root.txt`.

## Evidence

- `smbclient` with redacted credentials.
- `RU_config.xml` and the ADS `allinfo` output.
- `SHOWQUERY` with the encrypted password.
- `psexec` and `whoami` as SYSTEM.

## Lessons learned

- Anonymous shares can chain credentials incrementally.
- A Visual Basic project shipped to a client may include the decryption routine.
- NTFS alternate data streams hide data that `dir` does not show.
- A reporting service can leak LDAP configuration.

## Mitigations and detection

- Disable anonymous SMB and review permissions on `Data` and `Secure$`.
- Do not store passwords encrypted with a key embedded in the client.
- Audit alternate streams and remove secrets from debug files.
- Restrict HQK to administrators and do not return full configurations.
- Alert on `psexec`, created services and reads of `:Password:$DATA`.

## References

- <https://www.hackthebox.com/machines/Nest>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c54dec26-1551-4d3a-a0ea-4fa40f848eb3>
