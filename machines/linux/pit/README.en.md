---
machine: Pit
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, snmp, seeddms, cve-2019-12744, selinux, cockpit, privesc]
---

# Pit — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP with community `public` leaks the SeedDMS path and its 5.1.15 version. SeedDMS lets users upload PHP into `data/` and execute it; CVE-2019-12744 was fixed by adding a `.htaccess` that nginx ignores. The `nginx` shell reads `settings.xml` and logs in over SSH as `michelle`. An ACL on `/usr/local/monitoring` allows writing scripts that `/usr/bin/monitor` runs as root from SNMP extend.

## Recon

```bash
nmap -Pn -sSUV -p22,80,161,9090 <IP>
snmpwalk -v2c -c public <IP>
```

- `22` OpenSSH, `80` web, `161/udp` SNMP and `9090` Cockpit.
- SNMP reveals processes, paths and `/var/www/html/seeddms51x/seeddms`.
- The site is SeedDMS 5.1.15.

## Enumeration

With the path and version, look up CVE-2019-12744. The flaw lets users upload PHP files as documents and execute them from `data/`; the patch's `.htaccess` only works on Apache, not nginx. `settings.xml` holds the database and `michelle` credentials.

## Foothold

Upload a PHP file as a document and request `/data/1048576/<id>/1.php`. Execution confirms the webshell. A direct reverse shell fails because of SELinux; the webshell remains enough.

```text
/data/1048576/<id>/1.php?cmd=id
```

## Lateral movement

`settings.xml` reveals SeedDMS and system credentials. `michelle`'s password works over SSH. Cockpit on `9090` is another administration path.

## Privilege escalation

`getfacl /usr/local/monitoring` shows `michelle` can write to the directory. `/usr/bin/monitor` loops over `check*.sh` and runs them as root; SNMP extend invokes it. Write a script that adds a public key to `/root/.ssh/authorized_keys` and trigger it with `snmpwalk` on `NET-SNMP-EXTEND-MIB::nsExtendObjects`.

```bash
echo 'echo "<key>" | tee /root/.ssh/authorized_keys' > check_x.sh
snmpwalk -v1 -c public <IP> NET-SNMP-EXTEND-MIB::nsExtendObjects
```

## Evidence

- SNMP leaking the SeedDMS path.
- Webshell under `/data/1048576/`.
- `settings.xml` with credentials.
- Script in `monitoring` executed by SNMP as root.

## Lessons learned

- SNMP with a default community exposes paths and processes.
- A `.htaccess` does not protect `data/` when the server is nginx.
- SELinux can block a reverse shell without preventing command execution.
- A writable ACL on a directory of root-run scripts is root.

## Mitigation and detection

- Change the SNMP community and filter `161/udp`.
- Update SeedDMS, block PHP execution in `data/` and do not rely on `.htaccess` alone.
- Review ACLs on directories executed by root.
- Alert on new `check*.sh` files and on SNMP `nsExtend`.

## References

- [0xdf — Pit](https://0xdf.gitlab.io/2021/09/25/htb-pit.html)
- [IppSec — Pit](https://www.youtube.com/watch?v=IF5uhe1qR2I)
- [Hack The Box — Pit](https://app.hackthebox.com/machines/pit)
