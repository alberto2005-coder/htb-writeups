---
machine: Kotarak
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, tomcat, ajp, ghostcat, ssrf, wget, cve-2016-4971, privesc]
---

# Kotarak — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Tomcat exposes AJP and is vulnerable to Ghostcat, which allows reading files. SSRF in `url.php` reaches the internal manager, and a backup holds its credentials, which are used to deploy a WAR. A shell in the DMZ container yields `ntds.dit` and the SYSTEM hive, and `atanas`'s password. On the host, a cron runs `wget` as root; CVE-2016-4971 writes a `.wgetrc` that exfiltrates `/etc/shadow` and plants a root cron.

## Recon

```bash
nmap -Pn -sCV -p22,8009,8080,60000 <IP>
```

- `22` OpenSSH, `8009` AJP and `8080` Tomcat 8.5.5.
- `60000` is Kotarak's web host.
- The site has a URL proxy and a Tomcat manager.

## Enumeration

The `url.php` on `60000` fetches URLs and returns their content. `http://localhost:8080/manager/html` reaches the manager, and a container backup contains the credentials. Ghostcat (`CVE-2020-1938`) reads `WEB-INF/web.xml` and allows deploying a WAR with a webshell.

## Foothold

Upload a WAR with a JSP that runs commands and access it on port `8080`. The shell runs as Tomcat in the DMZ container.

```text
http://<IP>:8080/shell/shell.jsp?cmd=id
```

## Lateral movement

Copy `ntds.dit` and the SYSTEM hive from the container, extract them with `secretsdump.py` and recover `atanas`'s hash. The cracked password gives SSH access to the real host.

## Privilege escalation

The host runs `wget` as root from a cron. Wget 1.16 is vulnerable to CVE-2016-4971: on an HTTP redirect to FTP it saves the remote file under the original name. Serve a `.wgetrc` with `post_file = /etc/shadow` and `output_document = /etc/cron.d/wget-root-shell`; the next run exfiltrates the hash and writes a cron that returns a root shell.

```text
post_file = /etc/shadow
output_document = /etc/cron.d/wget-root-shell
```

## Evidence

- `WEB-INF/web.xml` read over AJP.
- WAR deployed and a Tomcat shell.
- `ntds.dit` and SYSTEM dumped.
- `.wgetrc` in root's home and a root cron shell.

## Lessons learned

- AJP must not be exposed or left without a `secret`.
- SSRF can reach Tomcat's manager on localhost.
- Container backups retain credentials and AD databases.
- An HTTP→FTP redirect in wget defeats filename validation.

## Mitigation and detection

- Close AJP or require `secret` and `address` on the connector.
- Upgrade Wget to 1.18 or later and never run it as root from cron.
- Restrict the manager to localhost and rotate backup credentials.
- Monitor `.wgetrc`, FTP redirects and writes to `/etc/cron.d`.

## References

- [0xdf — Kotarak](https://0xdf.gitlab.io/2021/05/19/htb-kotarak.html)
- [IppSec — Kotarak](https://www.youtube.com/watch?v=38e-sxPWiuY)
- [Hack The Box — Kotarak](https://app.hackthebox.com/machines/kotarak)
