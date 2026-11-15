---
machine: Oouch
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, oauth, csrf, uwsgi, dbus]
---

# Oouch — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An OAuth flow without `state` validation allows CSRF and linking someone else's account to the provider. Application access leads to SSH; uWSGI pivots to `www-data` and injection in the D-Bus iptables service yields root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
gobuster dir -u http://oouch.htb -w /usr/share/wordlists/dirb/common.txt
# OAuth flow without state
curl -i "http://oouch.htb/oauth/authorize?client_id=<ID>&redirect_uri=http://<IP>/callback"
# After SSH access
ss -lntp
busctl --system list
busctl call <SERVICE> <PATH> <IFACE> <METHOD> s "<PAYLOAD>"
```

## Enumeration

- Django application and OAuth server with authorization flows.
- Predictable or unvalidated `state` parameter.
- D-Bus service that executes iptables rules.

## Initial access

Start the OAuth flow and capture the callback. Without a valid `state`, force the victim to link the attacker's account; the token grants application access and an SSH key.

## Privilege escalation

uWSGI exposes a socket with weak permissions and allows code execution as `www-data`. The D-Bus service managing iptables locks concatenates arguments; inject a command and run as root.

## Evidence

- OAuth callback without `state` validation.
- Linked account and SSH access.
- D-Bus message with injection and root shell.

## Lessons learned

- `state` is the OAuth CSRF defense, not an optional detail.
- uWSGI sockets can be remote code execution.
- A D-Bus service building shell commands is injection.

## Mitigation and detection

- Validate `state` and use PKCE; reject callbacks without a session.
- Restrict uWSGI socket permissions.
- Use iptables APIs without a shell and validate arguments.

## References

- [0xdf — Oouch](https://0xdf.gitlab.io/2020/08/01/htb-oouch.html)
- [OAuth 2.0 — Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Hack The Box — Oouch](https://app.hackthebox.com/machines/oouch)
