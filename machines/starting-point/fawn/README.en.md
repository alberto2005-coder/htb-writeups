---
machine: Fawn
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/393
category: Starting Point
state: Retired
pwned: 2026-11-06
tags: [ftp, anonymous, misconfiguration]
---

# Fawn — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired · Starting Point · Linux · Very Easy

## TL;DR

The **FTP service (21/tcp)** allows **anonymous** access and exposes the flag in the server root directory. No exploitation is needed: just a login without credentials.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

Relevant result:

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
```

- Only exposed port: **21/tcp FTP** (`vsftpd 3.0.3`).
- No SSH or web services, so FTP is the main target.
- `vsftpd` often allows `anonymous` when the configuration has not been hardened.

## Enumeration

Check anonymous access:

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
```

If the server replies `230 Login successful`, anonymous access is enabled. List the contents:

```bash
ftp> ls -la
ftp> get flag.txt
ftp> bye
```

## Foothold

The flag sits directly in the FTP-served directory:

```bash
cat flag.txt
# <FLAG>
```

Non-interactive alternative:

```bash
wget -q ftp://anonymous:anonymous@<TARGET_IP>/flag.txt -O flag.txt
```

## Lessons learned

- **Anonymous FTP** is one of the first things to check when port 21 is open.
- `vsftpd` can expose the whole filesystem if `chroot` and least privilege are not enforced.
- FTP sends credentials and data in clear text; production should use SFTP/FTPS instead.
- In Starting Point the goal is to internalize the enumeration workflow, not to hunt for exploits.

## Mitigations and detection

**How to fix it:**

- Disable anonymous access (`anonymous_enable=NO`).
- Enforce **FTPS** (TLS) or migrate to **SFTP**.
- Apply `chroot_local_user=YES` and least-privilege permissions.
- Restrict access by IP and use dedicated accounts with strong passwords.

**How it would be detected:**

- Alerts for `anonymous` logins in the `vsftpd` logs.
- Monitoring of sensitive file downloads from the FTP server.
- Periodic scans that flag `Anonymous FTP login allowed`.

## References

- [vsftpd documentation](https://security.appspot.com/vsftpd.html)
- [OWASP — FTP Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1021 Remote Services](https://attack.mitre.org/techniques/T1021/)
