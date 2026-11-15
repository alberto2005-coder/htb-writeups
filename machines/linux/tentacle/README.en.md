---
machine: Tentacle
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, squid, wpad, opensmtpd, kerberos, keytab]
---

# Tentacle — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Several Squid proxies and a WPAD reveal internal networks; OpenSMTPD on one of them allows execution. Kerberos SSH authentication and a keytab grant more accounts; a backup script run as root completes the escalation.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,3128,8080 <IP>
curl -x http://<IP>:3128 http://<INTERNAL>/
# WPAD
curl -x http://<IP>:3128 http://wpad/wpad.dat
proxychains curl http://<INTERNAL>:25/
# Kerberos
kinit -kt <FILE>.keytab <USER>
ssh -K <USER>@<HOST>
find / -name "*.sh" -path "*backup*" 2>/dev/null
```

## Enumeration

- Squid on several ports and a WPAD file.
- OpenSMTPD reachable from an internal network.
- SSH with Kerberos, a keytab and a backup script.

## Initial access

Enumerate the proxies and use `proxychains` to reach the internal network. WPAD reveals the next proxy; OpenSMTPD is vulnerable to command execution and yields a host shell.

## Privilege escalation

The keytab allows Kerberos authentication and SSH access to another account. A backup script run as root is writable or uses a controllable path; modify it and obtain root.

## Evidence

- WPAD with the proxy chain.
- OpenSMTPD executing commands.
- Keytab, Kerberos SSH and modified backup.

## Lessons learned

- Internal proxies can be the only route into a network.
- Kerberos and keytabs are high-value credentials.
- A writable root backup script is direct execution.

## Mitigation and detection

- Restrict Squid and do not publish WPAD.
- Update OpenSMTPD and segment the network.
- Protect keytabs and backup scripts; run them unprivileged.

## References

- [0xdf — Tentacle](https://0xdf.gitlab.io/2021/06/19/htb-tentacle.html)
- [MIT Kerberos — keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [Hack The Box — Tentacle](https://app.hackthebox.com/machines/tentacle)
