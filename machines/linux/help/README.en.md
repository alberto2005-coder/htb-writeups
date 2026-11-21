---
machine: Help
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, graphql, helpdeskz, sqli, upload-bypass, kernel, cve-2017-16995, privesc]
---

# Help — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

There are two paths. The first enumerates a GraphQL API, obtains HelpDeskZ credentials and exploits an authenticated SQLi to dump the database, which yields SSH credentials. The alternative, which 0xdf considers the one most people used, is an unauthenticated upload bypass in HelpDeskZ: a PHP webshell is uploaded and the file path is brute-forced. For root, kernel exploits are tried: CVE-2017-16995 with `44298.c` and `45010.c`, and CVE-2017-5899 with the `s-nail-privsep` script; any of the three gives root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22`: OpenSSH 7.2p2 Ubuntu.
- `80`: Apache httpd 2.4.18 with HelpDeskZ.
- `3000`: Node.js Express, GraphQL API.

```bash
echo '<IP> help.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://help.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

Port `3000` exposes GraphQL. Introspection shows user and credential queries; a suitable query returns HelpDeskZ usernames and passwords.

```graphql
{ User { username password } }
```

Those credentials open HelpDeskZ, a ticketing application. Ticket search concatenates the parameter into SQL, allowing authenticated injection. `sqlmap` with the session cookie dumps the database and system credentials appear.

## Foothold

The alternative needs no credentials: HelpDeskZ 1.0.2 validates attachment extensions poorly. A PHP webshell is uploaded and the generated path under `uploads/tickets/` is found; the Exploit-DB script `40300.py` automates it.

```bash
searchsploit helpdeskz
python3 40300.py http://help.htb/support/uploads/tickets/ cmd.php
```

The webshell or the database credentials give a shell as `help`.

## Lateral movement

There is no second host. System enumeration shows the kernel version and user permissions. `help` has no `sudo`, so escalation depends on the kernel.

## Privilege escalation

The kernel is Ubuntu 4.4.0-116. Three exploits are tried:

- **CVE-2017-16995:** memory corruption in the BPF verifier; `44298.c` and `45010.c` compile and give root.
- **CVE-2017-5899:** directory traversal in the S-nail setuid helper; the `s-nail-privsep` script races the helper and leaves a setuid shell.

```bash
gcc -o a 44298.c && ./a
gcc -o a 45010.c && ./a
./a.sh
id
```

Any of the three paths ends with UID 0.

## Evidence

- GraphQL introspection and HelpDeskZ credentials.
- Authenticated SQLi and database dump.
- PHP webshell upload and execution.
- `uname -a` with kernel 4.4.0-116.
- Exploit execution and `id` with UID 0.

## Lessons learned

- Poorly protected GraphQL can expose complete credentials.
- An authenticated SQLi remains critical when the user can reach sensitive data.
- Extension or blocklist upload validation is easy to bypass.
- An old kernel turns a user shell into root with public exploits.
- CVE-2017-5899 is a S-nail issue, not a kernel one, even when grouped with escalation exploits.

## Mitigations and detection

- Disable introspection and limit GraphQL fields in production.
- Parameterize SQL queries and review ticket access.
- Validate uploads by content, allowed extension and destination outside the webroot.
- Update the kernel and apply security patches.
- Remove unnecessary SUID binaries such as the S-nail helper.
- Alert on GraphQL introspection queries, PHP uploads and kernel exploit execution.

## References

- [0xdf — Help](https://0xdf.gitlab.io/2019/06/08/htb-help.html)
- [IppSec — Help](https://www.youtube.com/watch?v=XB8CbhfOczU)
- [Hack The Box — Help](https://app.hackthebox.com/machines/help)
- [NVD — CVE-2017-16995](https://nvd.nist.gov/vuln/detail/CVE-2017-16995)
- [NVD — CVE-2017-5899](https://nvd.nist.gov/vuln/detail/CVE-2017-5899)
- [Knowledge — Escalation with CVE-2017-16995](../../../knowledge/linux/kernel-cve-2017-16995.en.md)
