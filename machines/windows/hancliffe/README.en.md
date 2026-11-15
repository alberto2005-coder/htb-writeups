---
machine: Hancliffe
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, uri-parsing, nuxeo, ssti, universal-remote, buffer-overflow, socket-reuse]
---

# Hancliffe — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A URI parsing flaw reaches an internal Nuxeo instance, vulnerable to Java SSTI and RCE. From there, Universal Remote runs commands as the next user. A password saved in Firefox moves to another user, and a development app on 9999 has a buffer overflow with socket reuse that ends in Administrator.

## Recon

```bash
nmap -Pn -sCV -p80,8000,9999 <IP>
```

- `80` nginx, `8000` HashPass and `9999` a banking app.
- `80` redirects to `hancliffe.htb`.
- `feroxbuster` enumerates paths and parameters.

## Enumeration

- The portal uses a URI parser that can confuse the host and reach an internal Nuxeo.
- Nuxeo exposes a Java template; an SSTI expression runs commands.
- The `9999` app is Universal Remote and runs commands as the user running it.

## Foothold

Exploit Nuxeo SSTI for a shell and enumerate the host. From that shell, reach Universal Remote and run a reverse shell as the next user.

```text
${7*7}
```

## Lateral movement

The Firefox profile has a saved password for `H@$hPa$$`; `firepwd` extracts it and allows `su` to the next user. That user can access the `9999` development app.

## Privilege escalation

`MyFirstApp.exe` on `9999` has a buffer overflow. Use a pattern for the offset, a `JMP ESP`, shellcode and socket reuse to read the second stage. The process runs as Administrator and the final shell is Administrator.

```text
python3 exploit.py <IP> 9999
```

## Evidence

- URI parsing and internal Nuxeo.
- Java SSTI and initial shell.
- Universal Remote and next user.
- Firefox `firepwd` and credentials.
- Buffer overflow with socket reuse and Administrator.

## Lessons learned

- A permissive URI parser can bypass host rules.
- Nuxeo with Java templates is SSTI/RCE.
- Universal Remote is remote execution by design.
- Firefox profiles store system credentials.

## Mitigation and detection

- Validate URIs and block internal destinations.
- Update Nuxeo and disable untrusted templates.
- Restrict Universal Remote and run it with least privilege.
- Protect browser profiles and enforce ASLR/DEP; review development binaries.

## References

- [0xdf — Hancliffe](https://0xdf.gitlab.io/2022/03/05/htb-hancliffe.html)
- [IppSec — Hancliffe](https://www.youtube.com/watch?v=kA-bkftyyY0)
- [Hack The Box — Hancliffe](https://app.hackthebox.com/machines/hancliffe)
