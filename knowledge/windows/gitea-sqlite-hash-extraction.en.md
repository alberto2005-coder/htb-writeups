---
topic: Extracción de hashes de Gitea
tags: [windows, gitea, sqlite, hashcat, credentials]
---

# Extracción de hashes de Gitea

**English** | [🇪🇸 Español](gitea-sqlite-hash-extraction.md)

## Concept

Gitea stores users and password hashes in a local SQLite database. If the service or a backup exposes `gitea.db`, PBKDF2 hashes can be extracted and cracked offline.

## When it applies

- Gitea installed on the same host as the compromised application.
- Backups or volumes with readable `gitea.db`.
- Gitea passwords reused by system accounts.

## Procedure

1. Locate `gitea.db` and confirm it is SQLite.
2. Dump the `user` table and the hash field.
3. Reformat the PBKDF2 hash for Hashcat.
4. Crack it and test the password against SSH/WinRM.

```bash
sqlite3 gitea.db '.tables'
sqlite3 gitea.db 'select name,passwd_hash from user;'
# Gitea format is pbkdf2$sha256$<iterations>$<salt>$<hash>
hashcat -m 10900 gitea.hash /usr/share/wordlists/rockyou.txt
```

## Variants

- MySQL/PostgreSQL in larger installations.
- Hash inside a Docker volume backup.
- Administrator account with a different hash.
- Password shared with the system user.

## Limitations

- The database must be readable by the compromised user.
- High PBKDF2 iteration counts slow cracking.
- The exact format changes across Gitea versions.

## Mitigation and detection

- Protect `gitea.db` and backups with restrictive permissions.
- Use unique passwords and slow hashes; rotate after an intrusion.
- Monitor database access and failed authentications.

## References

- <https://docs.gitea.com/administration/config-cheat-sheet>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://attack.mitre.org/techniques/T1552/001/>
