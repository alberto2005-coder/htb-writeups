---
topic: KeePass
tags: [windows, keepass, kdbx, password-manager, hashcat, key-file]
---

# KeePass

**English** | [🇪🇸 Español](keepass.md)

## Concept

KeePass stores credentials in a `.kdbx` database protected by a master password and, optionally, a key file. If an attacker obtains the database, they can try to crack the master password or use it to open the manager and extract every secret.

## When it applies

- `.kdbx` files in a profile or backup.
- A weak or reused master password.
- A key file next to the database.
- A KeePass process open on the host.

## Procedure

1. Locate the database and key file.
2. Extract the hash with `keepass2john`.
3. Crack with Hashcat when feasible.
4. Open the database with `kpcli` or KeePass.
5. Inventory and reuse credentials.

```bash
find / -iname '*.kdbx' 2>/dev/null
keepass2john database.kdbx > keepass.hash
hashcat -m 13400 keepass.hash wordlist.txt
kpcli --kdb database.kdbx
```

## Variants

- A database with a master password and key file.
- A hash extracted from memory or a backup.
- A master password reused from another service.
- Databases on network shares or repositories.

## Limitations

- A strong password makes cracking impractical.
- Without the key file the database does not open.
- KeePass versions change the format.
- The process may require interaction.

## Mitigation and detection

- Use strong, unique master passwords.
- Store the key file separately.
- Restrict access to `.kdbx` and backups.
- Alert on bulk access to managers and credential files.

## References

- <https://keepass.info/help/base/security.html>
- <https://github.com/openwall/john>
- <https://attack.mitre.org/techniques/T1555/005/>
