---
machine: Compromised
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, litecart, php, disable-functions, pam, backdoor, privesc]
---

# Compromised — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The box is already compromised: a LiteCart backup shows a backdoored login that writes credentials to an accessible file. Those credentials exploit LiteCart, but `disable_functions` blocks execution; MySQL and a UDF bypass it, and the `mysql` user has a shell. An `strace` log acts as a keylogger and yields `sysadmin`'s password. Two backdoors remain for root: a PAM module and an `LD_PRELOAD` in a SUID.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with LiteCart under `/shop`.
- The site is in production but keeps an accessible backup.
- `gobuster` finds `/shop/admin/` and backup files.

## Enumeration

- The backup contains a modified `login.php`: it records username and password in a file inside the webroot.
- Reading that file yields administrator credentials.
- `searchsploit litecart` shows the module-upload RCE.

## Foothold

Upload a malicious XML/PHP module, but `disable_functions` blocks `system`, `exec` and similar. Use a privileged MySQL account to create a UDF and run commands; the `mysql` user has a valid shell.

```sql
CREATE FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('id');
```

## Lateral movement

In `/var/log` or an `strace` file, the `mysql` execution shows the password on the command line. That password belongs to `sysadmin` and also works over SSH.

```bash
grep -a 'mysql' /var/log/* 2>/dev/null
ssh sysadmin@<IP>
```

## Privilege escalation

The previous attacker left two doors: a PAM module with a master password and an `LD_PRELOAD` in a SUID binary. The PAM module accepts a specific string for any user, including root.

```bash
strings /lib/security/pam_unix.so | grep -i backdoor
```

The alternative is using the `LD_PRELOAD` magic string as the current `passwd` password; the SUID binary interprets it and starts a shell without dropping privileges.

## Evidence

- LiteCart backup with a backdoored login.
- Credentials in a webroot file.
- `disable_functions` and MySQL UDF.
- `sysadmin` password in the `strace` log.
- PAM module and `LD_PRELOAD` as root.

## Lessons learned

- A public backup can contain vulnerable code and backdoors.
- `disable_functions` does not stop RCE when the database can load UDFs.
- `strace` logs and histories leak credentials.
- A compromised box may hold several backdoors; look for them.

## Mitigation and detection

- Do not leave backups or log files inside the webroot.
- Restrict `CREATE FUNCTION` and MySQL privileges.
- Audit PAM modules and SUID binaries with `LD_PRELOAD`.
- Rotate credentials and rebuild the host after a confirmed intrusion.

## References

- [0xdf — Compromised](https://0xdf.gitlab.io/2021/01/23/htb-compromised.html)
- [IppSec — Compromised](https://www.youtube.com/watch?v=yaV09XCDDqI)
- [Hack The Box — Compromised](https://app.hackthebox.com/machines/compromised)
