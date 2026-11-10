# Starting Point — Hack The Box

**English** | [🇪🇸 Español](README.md)

Hack The Box's beginner track: short boxes in linear tiers, each training **one service** and its typical misconfiguration. These are not retired Easy/Medium machines —those live in `machines/linux/` and `machines/windows/`— but guided exercises: the point is to build enumeration muscle memory before chaining vulnerabilities.

## How they are worked

1. Spawn the instance on the platform and connect to the VPN.
2. `nmap -Pn -sV -p-` against the IP: the surface is deliberately tiny.
3. Enumerate with the service's native client (`telnet`, `ftp`, `smbclient`, `redis-cli`, `mongo`, a browser…).
4. Abuse the default configuration and read the flag from the service or the filesystem.

## Notes

| Machine | Tier | OS | Service | Concept | ES | EN |
|---|---|---|---|---|---|---|
| Meow | 0 | Linux | 23/telnet | `root` with no password | [ES](meow/README.md) | [Ver](meow/README.en.md) |
| Fawn | 0 | Linux | 21/ftp | Anonymous access and `get flag.txt` | [ES](fawn/README.md) | [Ver](fawn/README.en.md) |
| Dancing | 0 | Windows | 445/smb | Null session and the `WorkShares` share | [ES](dancing/README.md) | [Ver](dancing/README.en.md) |
| Redeemer | 0 | Linux | 6379/redis | Redis without `AUTH` and `keys *` | [ES](redeemer/README.md) | [Ver](redeemer/README.en.md) |
| Explosion | 0 | Windows | 3389/rdp | `Administrator` with a blank password | [ES](explosion/README.md) | [Ver](explosion/README.en.md) |
| Preignition | 0 | Linux | 80/http | Hidden `/admin.php` and `admin:admin` | [ES](preignition/README.md) | [Ver](preignition/README.en.md) |
| Mongod | 0 | Linux | 27017/mongo | MongoDB without `--auth` | [ES](mongod/README.md) | [Ver](mongod/README.en.md) |
| Synced | 0 | Linux | 873/rsync | Anonymous module and `rsync` with no credentials | [ES](synced/README.md) | [Ver](synced/README.en.md) |
| Appointment | 1 | Linux | 80/http | Login SQLi with `' or '1'='1'#` | [ES](appointment/README.md) | [Ver](appointment/README.en.md) |
| Sequel | 1 | Linux | 3306/mysql | `root` with no password and `show databases` | [ES](sequel/README.md) | [Ver](sequel/README.en.md) |
| Crocodile | 1 | Linux | 21/ftp + 80/http | Anonymous FTP with user and password lists | [ES](crocodile/README.md) | [Ver](crocodile/README.en.md) |
| Responder | 1 | Windows | 80/http + 5985/winrm | LFI to UNC, NetNTLMv2 hash and WinRM | [ES](responder/README.md) | [Ver](responder/README.en.md) |
| Three | 1 | Linux | 80/http + S3 | Unauthenticated bucket and webshell | [ES](three/README.md) | [Ver](three/README.en.md) |
| Ignition | 1 | Linux | 80/http | Magento with `admin:qwerty123` | [ES](ignition/README.md) | [Ver](ignition/README.en.md) |
| Bike | 1 | Linux | 80/http | Handlebars SSTI up to root | [ES](bike/README.md) | [Ver](bike/README.en.md) |
| Funnel | 1 | Linux | 21/ftp + 22/ssh | SSH spray and a tunnel to internal PostgreSQL | [ES](funnel/README.md) | [Ver](funnel/README.en.md) |
| Pennyworth | 1 | Linux | 8080/http | Jenkins `root:password` and the Groovy console | [ES](pennyworth/README.md) | [Ver](pennyworth/README.en.md) |
| Tactics | 1 | Windows | 445/smb | Null session and a blank `Administrator` | [ES](tactics/README.md) | [Ver](tactics/README.en.md) |
| Archetype | 2 | Windows | 445/smb + 1433/mssql | SSIS config, `xp_cmdshell` and psexec | [ES](archetype/README.md) | [Ver](archetype/README.en.md) |
| Oopsie | 2 | Linux | 80/http | Cookie IDOR, upload and a SUID with `PATH` | [ES](oopsie/README.md) | [Ver](oopsie/README.en.md) |
| Vaccine | 2 | Linux | 21/ftp + 80/http | Backup, SQLi with `--os-shell` and `sudo vi` | [ES](vaccine/README.md) | [Ver](vaccine/README.en.md) |
| Unified | 2 | Linux | 8443/https | Log4Shell on UniFi and MongoDB 27117 | [ES](unified/README.md) | [Ver](unified/README.en.md) |
| Included | 2 | Linux | 80/http + 69/udp | LFI, unauthenticated TFTP and the `lxd` group | [ES](included/README.md) | [Ver](included/README.en.md) |
| Markup | 2 | Windows | 80/http + 22/ssh | XXE to `id_rsa` and a scheduled `job.bat` | [ES](markup/README.md) | [Ver](markup/README.en.md) |
| Base | 2 | Linux | 80/http | `strcmp` with arrays, upload and `sudo find` | [ES](base/README.md) | [Ver](base/README.en.md) |

> **Tiers:** Tier 0 is the first eight (Meow → Synced) and is complete. Tier 1 is Appointment → Tactics (nine) and Tier 2 is Archetype → Base (seven). Total: **25 notes**, all in ES/EN.

## Cross-cutting lessons

- The service that answers "without credentials" **is** the finding: SMB null session, anonymous FTP, open Redis, MongoDB without `--auth`, Telnet with a blank `root` password, an S3 bucket without IAM.
- Every protocol has its client: `smbclient -L //IP -N`, `ftp` with `anonymous`, `redis-cli`, `mongosh`, `xfreerdp /cert:ignore`, `aws --endpoint`.
- The flag rarely needs escalation: it sits in the share, the database or the administrator's desktop. In Tier 2 the user-to-root step appears.
- The same services reappear on Easy/Medium boxes, there with one more enumeration step.

## Reference mitigations

- SMB: signing and encryption, SMBv1 disabled, null sessions removed, admin shares restricted by group.
- FTP: no `anonymous`; SFTP/FTPS with named accounts.
- Telnet: remove it; SSH with strong passwords and `PermitRootLogin no`.
- Redis and MongoDB: `requirepass`/`--auth`, loopback bind and per-database ACLs.
- RDP: no blank passwords, NLA required and MFA.
- Web: prepared queries, no `eval` or templates with user input, uploads outside the webroot.
- Detection: 4624 type 3 with anonymous NTLM, `230 Login successful` for `anonymous`, `INFO`/`keys *` without `AUTH`, `show dbs` without authentication and `PUT` to buckets from unusual IPs.
