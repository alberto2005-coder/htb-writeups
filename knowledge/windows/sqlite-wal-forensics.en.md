---
topic: SQLite — recovery with WAL and SHM
tags: [windows, sqlite, wal, forensics, sticky-notes]
---

# SQLite — recovery with WAL and SHM

**English** | [🌐 Español](sqlite-wal-forensics.md)

## Concept

SQLite in WAL mode writes transactions to a `-wal` file and uses `-shm` for the shared index. Copying only the main database misses recent data. Copying all three files allows opening the database and recovering records the application has not checkpointed, such as credentials or notes.

## When it applies

- A desktop application SQLite database is found.
- `-wal` and `-shm` files exist next to it.
- The main database looks incomplete or lacks recent entries.

## Procedure

1. Copy the database and its `-wal`/`-shm` files to the same directory.
2. Open it with `sqlite3` and list tables.
3. Force a checkpoint or query the tables directly.
4. Look for credentials, notes and paths.

## Commands

```bash
cp StickyNotes.snt StickyNotes.snt-wal StickyNotes.snt-shm /tmp/
sqlite3 /tmp/StickyNotes.snt ".tables"
sqlite3 /tmp/StickyNotes.snt "PRAGMA wal_checkpoint(FULL);"
sqlite3 /tmp/StickyNotes.snt "SELECT * FROM <TABLE>;"
```

## Variants

- Use `sqlite3 .recover` if the database is corrupt.
- Search the WAL with `strings`.
- Apply the same technique to browser and Electron databases.

## Limitations

- The WAL may be encrypted or empty.
- The application may have checkpointed and deleted it.
- The SQLite version must be compatible.

## Mitigation

- Encrypt databases with sensitive data.
- Delete WAL/SHM on close and restrict read access.
- Do not store plaintext credentials.

## Detection

- Access to `-wal`/`-shm` outside the application.
- Copies of desktop databases.
- Queries against credential tables.

## References

- [SQLite — WAL format](https://www.sqlite.org/wal.html)
- [0xdf — Breadcrumbs](https://0xdf.gitlab.io/2021/07/17/htb-breadcrumbs.html)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
