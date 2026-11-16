---
machine: Reactor
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, nextjs, react2shell, cve-2025-55182, sqlite, node-inspector, privesc]
---

# Reactor — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site is NextJS 15.0.3 with React 19 RC and is vulnerable to React2Shell (CVE-2025-55182): a multipart payload in a Server Action deserializes data and runs code as `node`. The app's SQLite database contains MD5 hashes; crack `engineer` and reuse the password for the system account. An uptime monitor runs as root with the Node inspector on localhost:9229; an SSH tunnel and the DevTools protocol run code in that process and reach root.

## Recon

```bash
nmap -Pn -sCV -p22,3000 <IP>
```

- `22` OpenSSH 9.6 and `3000` NextJS.
- Headers `x-nextjs-cache`, `x-nextjs-prerender` and `X-Powered-By: Next.js`.
- The app is a reactor monitoring dashboard.

## Enumeration

Download the JS chunks and look for versions. NextJS is 15.0.3 and React 19.0.0-rc; the combination is vulnerable to CVE-2025-55182. Identify a Server Action and build a multipart body with the `Next-Action` header.

## Foothold

The React2Shell payload deserializes an object with a prototype chain reaching `child_process.execSync`. Send it with `curl` and get execution as `node`; a reverse shell or base64 command stabilizes access.

```bash
# React2Shell
curl -X POST http://<IP>:3000/ -H 'Next-Action: <ACTION>' \
  -H 'Content-Type: multipart/form-data; boundary=----R2S' --data-binary @r2s-body.txt
# root inspector
ssh -L 9229:localhost:9229 engineer@<IP>
node inspect 127.0.0.1:9229
```

## Lateral movement

`/opt/reactor-app/reactor.db` contains a `users` table with MD5 hashes. Crack `engineer` and the password works in the app, with `su engineer` and over SSH.

## Privilege escalation

`ps` shows a root uptime monitor with `node --inspect=127.0.0.1:9229`. Reconnect SSH with `-L 9229:localhost:9229`, attach the inspector and evaluate code in the root process; for example, copy bash and set SUID or write a key to `/root/.ssh`.

## Evidence

- Vulnerable NextJS/React versions.
- RSC payload and `node` shell.
- SQLite with `engineer` hash.
- Node inspector on localhost as root.

## Lessons learned

- Framework versions leak in chunks and headers.
- RSC processes client data and must be treated as untrusted.
- App MD5 hashes get reused for system accounts.
- A Node inspector exposed on localhost is root execution if it can be tunneled.

## Mitigation and detection

- Update React/NextJS to fixed versions.
- Validate and sign Server Action payloads.
- Use Argon2/bcrypt and unique passwords per account.
- Do not run monitors with `--inspect` as root; restrict 9229.

## References

- [0xdf — Reactor](https://0xdf.gitlab.io/2026/10/03/htb-reactor.html)
- [IppSec — Reactor](https://www.youtube.com/watch?v=-mBxWU9vrJQ)
- [Hack The Box — Reactor](https://app.hackthebox.com/machines/reactor)
