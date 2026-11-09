# Starting Point — Hack The Box

**English** | [🇪🇸 Español](README.md)

Machines from Hack The Box's **Starting Point** track. They come in three linear tiers (0, 1 and 2) and are not "regular" boxes: each one trains a single service or technique. Every note in this category lives **only** in this directory; retired Easy/Medium machines sit in `machines/linux/` and `machines/windows/` by OS.

## Notes

| Machine | OS | Concept | Status | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | FTP and Telnet with no credentials | 100% | [ES](meow/README.md) | [Ver](meow/README.en.md) |
| Fawn | Linux | Anonymous FTP | 100% | [ES](fawn/README.md) | [Ver](fawn/README.en.md) |
| Dancing | Windows | SMB with a null session | 100% | [ES](dancing/README.md) | [Ver](dancing/README.en.md) |
| Redeemer | Linux | Unauthenticated Redis | 100% | [ES](redeemer/README.md) | [Ver](redeemer/README.en.md) |
| Explosion | Windows | RDP with a blank password | pending | [ES](explosion/README.md) | [Ver](explosion/README.en.md) |
| Preignition | Linux | Hidden panel and default credentials | pending | [ES](preignition/README.md) | [Ver](preignition/README.en.md) |
| Mongod | Linux | MongoDB without `--auth` | pending | [ES](mongod/README.md) | [Ver](mongod/README.en.md) |
| Synced | Linux | Anonymous rsync | pending | [ES](synced/README.md) | [Ver](synced/README.en.md) |
| Sequel | Linux | MySQL with passwordless `root` | pending | [ES](sequel/README.md) | [Ver](sequel/README.en.md) |

> "100%" and "pending" reflect the HTB profile, not whether the note exists. Every note in the table is written.

## How they are solved

1. `nmap -sC -sV` and record the **version** of each service.
2. Talk to the service with its own client (`ftp`, `smbclient`, `redis-cli`, `mongosh`, `rsync`, `mysql`, `xfreerdp`).
3. Check blank passwords, anonymous access and hidden panels before hunting for exploits.
4. The flag is usually a desktop file, a collection or a table row.

## Pending

- Confirm each machine's exact tier on the platform and add it to the table.
- Fill in the remaining tier 1 and 2 boxes (Appointment, Crocodile, Responder, Three, Ignition, Bike, Pennyworth, Tactics, Archetype, Oopsie, Vaccine…).
