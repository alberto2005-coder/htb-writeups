# Starting Point — Hack The Box

**English** | [🇪🇸 Español](README.md)

Hack The Box's beginner track: short boxes in linear tiers, each training **one service** and its typical misconfiguration. These are not retired Easy/Medium machines —those live in `machines/linux/` and `machines/windows/`— but guided exercises: the point is to build enumeration muscle memory before chaining vulnerabilities.

## How they are worked

1. Spawn the instance on the platform and connect to the VPN.
2. `nmap -Pn -sV -p-` against the IP: the surface is deliberately tiny.
3. Enumerate with the service's native client (`telnet`, `ftp`, `smbclient`, `redis-cli`, `mongo`, a browser…).
4. Abuse the default configuration and read the flag from the service or the filesystem.

## Notes

| Machine | OS | Service | Concept | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | 23/telnet | `root` with no password | [ES](meow/README.md) | [Ver](meow/README.en.md) |
| Fawn | Linux | 21/ftp | Anonymous access and `get flag.txt` | [ES](fawn/README.md) | [Ver](fawn/README.en.md) |
| Dancing | Windows | 445/smb | Null session and the `WorkShares` share | [ES](dancing/README.md) | [Ver](dancing/README.en.md) |
| Redeemer | Linux | 6379/redis | Redis without `AUTH` and `keys *` | [ES](redeemer/README.md) | [Ver](redeemer/README.en.md) |
| Explosion | Windows | 3389/rdp | `Administrator` with a blank password | [ES](explosion/README.md) | [Ver](explosion/README.en.md) |
| Preignition | Linux | 80/http | Hidden `/admin.php` and `admin:admin` | [ES](preignition/README.md) | [Ver](preignition/README.en.md) |
| Mongod | Linux | 27017/mongo | MongoDB without `--auth` | [ES](mongod/README.md) | [Ver](mongod/README.en.md) |
| Synced | Linux | 873/rsync | Anonymous module and `rsync` with no credentials | [ES](synced/README.md) | [Ver](synced/README.en.md) |
| Sequel | Linux | 3306/mysql | `root` with no password and `show databases` | [ES](sequel/README.md) | [Ver](sequel/README.en.md) |

> **Tiers:** the first eight (Meow → Synced) are Tier 0; **Sequel** is Tier 1 and still belongs in this section. All nine are here.

## Cross-cutting lessons

- The service that answers "without credentials" **is** the finding: SMB null session, anonymous FTP, open Redis, MongoDB without `--auth`, Telnet with a blank `root` password.
- Every protocol has its client: `smbclient -L //IP -N`, `ftp` with `anonymous`, `redis-cli`, `mongosh`, `xfreerdp /cert:ignore`.
- The flag rarely needs escalation: it sits in the share, the database or the administrator's desktop.
- The same services reappear on Easy/Medium boxes, there with one more enumeration step.

## Reference mitigations

- SMB: signing and encryption, SMBv1 disabled, null sessions removed, admin shares restricted by group.
- FTP: no `anonymous`; SFTP/FTPS with named accounts.
- Telnet: remove it; SSH with strong passwords and `PermitRootLogin no`.
- Redis and MongoDB: `requirepass`/`--auth`, loopback bind and per-database ACLs.
- RDP: no blank passwords, NLA required and MFA.
- Detection: 4624 type 3 with anonymous NTLM, `230 Login successful` for `anonymous`, `INFO`/`keys *` without `AUTH`, and `show dbs` without authentication.
