---
machine: Intuition
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, file-read, ftp, suricata, ansible, privesc]
---

# Intuition — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Several vhosts surround a document compressor. XSS in bug reports gives developer and then admin access; the dashboard exports PDFs with a `urllib` file read, leaking FTP credentials and a `dev_acc` SSH key. Suricata logs expose `lopez`'s password, and `lopez` can run `runner2` as root; the binary calls `ansible-galaxy` with a controlled name and allows command injection.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with `comprezzor.htb`.
- `ffuf` finds `auth.comprezzor.htb`, `report.comprezzor.htb` and `admin.comprezzor.htb`.
- The main site compresses documents and reports allow screenshots.

## Enumeration

- Bug reports reflect HTML and run XSS when a developer reviews them.
- Steal `dev_acc`'s session and reach a panel that exports reports to PDF.
- The export uses `urllib` with a controlled URL; a `file://` path reads server files.

## Foothold

Read the FTP credentials and `dev_acc`'s private key. Use the key over SSH.

```bash
ssh -i dev_acc.key dev_acc@comprezzor.htb
```

## Lateral movement

Suricata logs traffic and cleartext credentials. The logs contain `lopez`'s password, which works over SSH.

```bash
grep -R "password" /var/log/suricata/
ssh lopez@comprezzor.htb
```

## Privilege escalation

`lopez` can run `/opt/runner2/runner2` as root. The binary reads JSON and calls `ansible-galaxy role install` with the role name; a semicolon in the name injects a command.

```bash
echo '{"role": "x; bash"}' > /tmp/r.json
sudo /opt/runner2/runner2 /tmp/r.json
```

## Evidence

- XSS in reports and session theft.
- `urllib` file read and FTP credentials.
- `dev_acc` SSH key.
- Suricata logs and `lopez`.
- `runner2`, `ansible-galaxy` and root.

## Lessons learned

- XSS in an internal panel can expose more vhosts.
- `urllib` with unvalidated schemes is file read.
- IDS logs can contain cleartext credentials.
- A wrapper calling `ansible-galaxy` with controlled input is injection.

## Mitigation and detection

- Escape reports and use CSP.
- Validate schemes and hosts in exports.
- Redact credentials in logs and restrict Suricata.
- Use role allowlists and `escapeshellarg`.

## References

- [0xdf — Intuition](https://0xdf.gitlab.io/2024/09/14/htb-intuition.html)
- [IppSec — Intuition](https://www.youtube.com/watch?v=uUPj4Qj01-0)
- [Hack The Box — Intuition](https://app.hackthebox.com/machines/intuition)
