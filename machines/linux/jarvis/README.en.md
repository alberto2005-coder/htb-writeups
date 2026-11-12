---
machine: Jarvis
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, phpmyadmin, cve-2018-12613, systemctl, suid]
---

# Jarvis — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The booking site is injectable and leaks phpMyAdmin credentials. The vulnerable phpMyAdmin version allows LFI/RCE and a shell. A SUID `systemctl` binary completes the escalation to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,64999 <IP>
```

Add `supersecurehotel.htb` to hosts. The admin panel runs on port 64999 and exposes phpMyAdmin.

## Initial access

The room parameter is injectable. Use `sqlmap` or a manual payload to extract users and hashes:

```bash
sqlmap -r room.txt --batch --dbs
```

The credentials log in to phpMyAdmin. The version is vulnerable to CVE-2018-12613 (LFI in `index.php`), allowing local file inclusion or code execution when a path is controlled.

## Lateral movement

Use the LFI to read configuration and find a reused credential. A PHP file can also be written to an included path and executed:

```bash
curl 'http://<IP>:64999/index.php?target=db_sql.php%253f/../../../../etc/passwd'
```

This returns a shell as `www-data`.

## Privilege escalation

```bash
find / -perm -4000 -type f 2>/dev/null
```

A SUID `systemctl` is found. Abuse it to start a service or run a command as root:

```bash
systemctl --version
```

With SUID `systemctl`, start a controlled unit or invoke `ExecStart` with a custom binary; the resulting process is root.

## Evidence

- SQLi request and redacted dump.
- phpMyAdmin access and version.
- LFI and shell.
- SUID `systemctl` and root shell.

## Lessons learned

- SQLi in a secondary panel can expose the database.
- Old phpMyAdmin is an LFI/RCE target.
- SUID `systemctl` is direct escalation.
- Check high ports, not just 80/443.

## Mitigation and detection

- Parameterise queries and limit errors.
- Update phpMyAdmin and restrict exposure.
- Remove unnecessary SUID bits.
- Monitor unit creation and root processes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2018-12613>
- <https://www.hackthebox.com/machines/jarvis>
- <https://gtfobins.github.io/gtfobins/systemctl/>
