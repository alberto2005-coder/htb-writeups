---
machine: Gofer
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, smb, ssrf, gopher, phishing, suid, privesc]
---

# Gofer — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An anonymous SMB share holds an email with hints: a proxy in development and a phishing-prone user. `proxy.gofer.htb` only blocks GET but accepts POST with `url`, enabling gopher SSRF. Send an internal email with a malicious ODT, get `jhudson`, and `tcpdump` captures `tbuckley`'s basic auth. The SUID `notes` has a use-after-free that grants the admin role and runs `tar` without an absolute path, giving root through PATH hijacking.

## Recon

```bash
nmap -Pn -sCV -p22,25,80,445 <IP>
```

- `22` SSH, `25` SMTP/Postfix, `80` Apache and `445` Samba.
- `smbclient -N //<IP>/shares` reads an anonymous share.
- `ffuf` with `Host: FUZZ.gofer.htb` discovers `proxy.gofer.htb`.

## Enumeration

- The share contains `.backup/mail`, an internal email mentioning phishing, ODT and an unrestricted proxy.
- The proxy returns 401 for GET, but POST/OPTIONS to `/index.php` return 200.
- `index.php?url=` accepts gopher, does not block `gofer.htb` and allows newline injection with double URL-encoding.

## Foothold

Use gopher to talk to SMTP on localhost and send `jhudson` an email linking to an ODT that runs a macro when opened. The user downloads it and a shell as `jhudson` follows.

```text
gopher://127.0.0.1:25/_HELO%20x%250d%250aMAIL%20FROM...
```

## Lateral movement

`jhudson` is in `netdev` and `tcpdump` has capabilities, so local traffic can be captured. Filter HTTP requests and the proxy's `Authorization: Basic` header appears; decode it and `tbuckley`'s password works over SSH.

```bash
tcpdump -i any -nn -A 'tcp port 80 and (tcp[((tcp[12:1] & 0xF0) >> 2):4] = 0x47455420)'
```

## Privilege escalation

`notes` is root SUID/SGID and only the `dev` group, which includes `tbuckley`, can run it. After creating and deleting a user, the freed pointer is reused as the note buffer; 24 bytes of padding write `admin` into the role. Option 8 runs `tar -czvf ...` without an absolute path; place a malicious `tar` in `.` and prepend it to `PATH`.

```bash
export PATH=.:$PATH
printf '#!/bin/bash\nbash -i\n' > tar && chmod +x tar
notes
```

## Evidence

- Share email and proxy gopher SSRF.
- ODT macro and `jhudson` shell.
- `tcpdump` capturing `tbuckley`'s Basic header.
- Use-after-free in `notes`, admin role and hijacked `tar`.

## Lessons learned

- Forgotten SMB shares leak context and usernames.
- Restricting only GET does not protect a proxy.
- A SUID with in-memory role checks and pathless `system` is direct escalation.

## Mitigation and detection

- Close anonymous shares and review internal email.
- Validate method and scheme in the proxy; block gopher and internal destinations.
- Fix the use-after-free and use absolute paths in privileged binaries.

## References

- [0xdf — Gofer](https://0xdf.gitlab.io/2023/10/28/htb-gofer.html)
- [IppSec — Gofer](https://www.youtube.com/watch?v=waKs935HxNE)
- [Hack The Box — Gofer](https://app.hackthebox.com/machines/gofer)
