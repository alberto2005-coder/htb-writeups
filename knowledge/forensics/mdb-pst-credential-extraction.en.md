---
topic: Microsoft Access and Outlook — credential extraction
tags: [forensics, access, mdb, pst, credentials]
---

# Microsoft Access and Outlook — credential extraction

**English** | [🌐 Español](mdb-pst-credential-extraction.md)

## Concept

Legacy Microsoft Access backups (`*.mdb`) and exported Outlook mailboxes (`*.pst`) often retain credentials in tables and messages. They are common on backup shares and support workstations, and can turn an anonymously reachable file into a valid account without exploiting a service.

## When it applies

- FTP, SMB or an accessible backup provides `.mdb`, `.pst` or old ZIP files.
- The application uses Access as an internal database or stores exported mail.
- Credentials are likely reused on telnet, SSH, RDP or internal panels.

## Procedure

1. Identify the files with `file` and list the MDB tables with `mdb-tables`.
2. Export user tables with `mdb-export` and review hashes or cleartext passwords.
3. If the ZIP is protected, try the password recovered from the database before attacking it.
4. Convert the PST with `readpst` and search for welcome mail, credentials and configuration.

## Commands

```bash
file backup.mdb "Access Control.zip"
mdb-tables -1 backup.mdb
mdb-export backup.mdb auth_user
readpst -o pst -S "Access Control.pst"
grep -RniE "password|passwd|credential|username" pst | head
```

## Variants

- `mdb-sql` for targeted queries and `mdb-export` for a full table dump.
- `pffexport` or `libpff` when `readpst` fails on a damaged PST.
- `strings` over the MDB or PST for a quick first pass.

## Limitations

- An MDB can have a database password, but many tools ignore it.
- A PST password does not encrypt the content: it only gates opening it in Outlook.
- Not every message is readable if the PST is corrupt or uses an encrypted profile.

## Mitigation

- Remove mail exports and database backups from accessible shares.
- Apply least privilege and encryption to backups; do not reuse passwords.
- Look for `.mdb` and `.pst` files in repositories and support workstations.

## Detection

- Unexpected access to `.mdb`, `.pst` or backup ZIP files.
- Execution of `mdb-export`, `readpst` or forensic tools on a production host.
- Authentications with the same password from a new source.

## References

- [0xdf — Access](https://0xdf.gitlab.io/2019/03/02/htb-access.html)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
- [MDB Tools](https://www.mdbtools.ca/)
