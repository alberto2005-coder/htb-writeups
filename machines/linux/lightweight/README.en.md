---
machine: Lightweight
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ldap, tcpdump, backup, openssl, capabilities]
---

# Lightweight — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The website creates an SSH account on visit. LDAP activity is generated and cleartext credentials are captured on localhost with `tcpdump`, pivoting to the first user. A backup is cracked for the next user; root comes from full capabilities assigned to an OpenSSL copy.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,389 <IP>
curl -s http://lightweight.htb/
ssh <USER>@<IP>
# Loopback LDAP capture
tcpdump -i lo -A -s0 port 389
# Backup
zip2john backup.zip > hash.txt
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
# Capabilities
getcap -r / 2>/dev/null
./openssl_cap setuidgid 0 /bin/sh -c id
```

## Enumeration

- Site that automatically registers an SSH account.
- LDAP on localhost with simple authentication.
- Protected backup and an `openssl` copy with capabilities.

## Initial access

Log in with the account created by the website. Starting a session generates LDAP traffic; `tcpdump` on the loopback interface captures the bind in cleartext and reveals another user password.

## Privilege escalation

Crack the second user backup with John. With that account, enumerate capabilities and find an OpenSSL copy with `cap_setuid`/`cap_setgid`; use it to launch a shell with UID 0.

## Evidence

- SSH account created from the website.
- LDAP capture with cleartext credentials.
- Cracked backup and `openssl` with capabilities running `id`.

## Lessons learned

- Simple LDAP sends credentials unencrypted.
- Local backups are password dictionaries.
- A capability on a copied binary breaks least privilege.

## Mitigation and detection

- Require LDAPS or SASL and avoid simple binds.
- Encrypt backups and restrict read access.
- Audit `getcap -r /` and remove copied binaries with capabilities.

## References

- [0xdf — Lightweight](https://0xdf.gitlab.io/2019/05/11/htb-lightweight.html)
- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Hack The Box — Lightweight](https://app.hackthebox.com/machines/lightweight)
