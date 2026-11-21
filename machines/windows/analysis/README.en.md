---
machine: Analysis
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, ldap, active-directory, webshell, hta, snort, privesc]
---

# Analysis — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The PHP site on `analysis.htb` queries Active Directory over LDAP with a controllable parameter. LDAP injection enumerates users and reads the `description` field of a shared account, which holds the internal panel password. The dashboard accepts a PHP webshell or an HTA file to execute code as `svc_web`. `jdoe`'s credentials appear in the autologon registry values and, as an alternative, in the `alert_panel.php` web logs. WinRM provides a session as `jdoe`. For Administrateur, a malicious DLL is written to Snort's dynamic preprocessor directory, which Snort loads with elevated privileges.

## Reconnaissance

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985 <IP>
```

- `53`, `88`, `389`, `636`, `3268` and `3269`: DNS, Kerberos and LDAP on a domain controller.
- `80`: IIS serving the main site.
- `445` and `139`: SMB.
- `5985`: WinRM, useful once credentials are obtained.
- The domain is `analysis.htb` and the host is `DC-ANALYSIS`.

```bash
echo '<IP> analysis.htb internal.analysis.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://analysis.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The public site is a corporate page. The `internal.analysis.htb` vhost hosts a dashboard with a user search form. The query is built against LDAP and the `name` parameter accepts wildcards: `name=b*` returns more results than `name=b`, confirming that `*` is interpreted inside the filter.

Wildcards enumerate domain users and read attributes such as `description`. A shared account stores its password there, which opens the internal dashboard.

## Foothold

The dashboard supports file uploads. The direct path is a PHP webshell in the upload directory; the alternative is an HTA file that executes when opened from the panel. Either one yields code execution as `svc_web` on `DC-ANALYSIS`.

```text
name=*
name=*)(description=*
```

Later host enumeration shows IIS, PHP and a Snort installation.

## Lateral movement

`svc_web` cannot read the other users' home directories. There are two sources of `jdoe` credentials:

1. **Autologon:** under `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`, the `DefaultUserName` and `DefaultPassword` values are in clear text.
2. **Web logs:** `alert_panel.php` receives a username and password over GET and writes them to the IIS log. The `W3SVC2` log contains requests with `jdoe`'s credentials.

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' |
  Select-Object DefaultDomainName, DefaultUserName, DefaultPassword
findstr alert_panel.php C:\inetpub\logs\LogFiles\W3SVC2\u_ncsa1.log
```

Those credentials open a WinRM session:

```bash
evil-winrm -i analysis.htb -u jdoe -p '<PASSWORD>'
```

## Privilege escalation

`C:\Snort\etc\snort.conf` loads dynamic preprocessors from `C:\Snort\lib\snort_dynamicpreprocessor`. The folder ACL lets `BUILTIN\Users` create files and directories. Snort runs with elevated privileges and loads DLLs from that directory, so a DLL that performs a privileged action is compiled and dropped there. Reloading or restarting the service loads the DLL in Snort's context and the escalation leads to `Administrateur`.

```powershell
icacls C:\Snort\lib\snort_dynamicpreprocessor
# BUILTIN\Users:(CI)(AD) and (WD)
```

## Evidence

- Different responses when using `*` in the `name` parameter.
- Username and password read from the `description` attribute.
- Dashboard access and `whoami` as `svc_web`.
- `jdoe` credentials in the registry and the IIS log.
- `whoami /priv` and a WinRM session as `jdoe`.
- Writable ACL on the Snort directory and DLL load.
- `whoami` as `administrateur`.

## Lessons learned

- An LDAP filter built by concatenation allows enumerating the whole directory.
- `description` and `info` attributes often hold operational secrets.
- Autologon credentials and logs with GET parameters are common leaks.
- A plugin or preprocessor directory writable by users is privileged code execution.
- File uploads must validate extension, content and destination, not just `Content-Type`.

## Mitigations and detection

- Parameterize LDAP queries and escape `*`, `(`, `)` and `\`.
- Do not store passwords in directory attributes; use managed service accounts.
- Restrict read access to `description` and audit changes.
- Disable cleartext autologon passwords or use LSA secrets.
- Never log credentials in URLs; review IIS logs and restrict access to them.
- Apply least-privilege ACLs to Snort, plugin and service directories.
- Alert on DLL writes under service paths and on Snort loads outside maintenance.

## References

- [0xdf — Analysis](https://0xdf.gitlab.io/2024/06/01/htb-analysis.html)
- [IppSec — Analysis](https://www.youtube.com/watch?v=9U7OFdri73g)
- [Hack The Box — Analysis](https://app.hackthebox.com/machines/analysis)
- [Knowledge — LDAP injection in Active Directory](../../../knowledge/windows/ldap-injection-ad.en.md)
