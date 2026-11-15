---
title: daloRADIUS — SNMP discovery and default credentials
tags: [linux, snmp, daloradius, radius, default-credentials]
---

# daloRADIUS — SNMP discovery and default credentials

[🇪🇸 Español](daloradius-default-creds.md) | **English**

## Concept

daloRADIUS is a web management UI for FreeRADIUS. Many installations keep the `administrator` user and a default password, and the portal is discovered through SNMP strings or a vhost. Inside, the user table may hold hashes reusable over SSH.

## When it applies

- `161/udp` answers with the `public` community.
- `snmpwalk` mentions `daloradius`, `radius` or a `/daloradius` path.
- The portal is on an internal port or a vhost.

## Procedure

1. Enumerate SNMP and extract strings and processes.
2. Locate the portal and try documented credentials.
3. Review users, attributes and hashes.
4. Crack and try the password over SSH.

```bash
snmpwalk -v2c -c public <IP> | grep -i -E 'daloradius|radius|http'
curl -s http://<IP>/daloradius/login.php
```

## Variants

- The portal may listen only on `127.0.0.1`; use an SSH tunnel.
- Hashes may be MD5, SHA1 or NT; identify with `hashid`.
- The MySQL database may be reachable with the portal credentials.

## Limitations

- The SNMP community may differ from `public`.
- Default credentials may have been changed.
- The portal may require HTTPS or a specific vhost.

## Mitigation and detection

- Change default credentials and use MFA.
- Restrict SNMP and portal access to the management network.
- Store passwords with bcrypt/Argon2 and never reuse them.
- Audit logins and queries to the user table.

## References

- <https://github.com/lirantal/daloradius>
- <https://www.daloradius.com/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html>
