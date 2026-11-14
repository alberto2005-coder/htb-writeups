---
topic: NSS PostgreSQL — jail users and escalation
tags: [linux, nss, postgresql, jail, privesc]
---

# NSS PostgreSQL — jail users and escalation

**English** | [🌐 Español](nss-postgresql-jail.md)

## Concept

A jail can delegate users and groups to PostgreSQL through an NSS module. If database credentials are in a readable file, an attacker can insert users with UID 0 or the `sudo` GID. System authentication trusts those rows as if they were `/etc/passwd` and `/etc/shadow`.

## When it applies

- `/etc/nsswitch.conf` uses a module such as `nss-pgsql` for `passwd` or `shadow`.
- The `nss-pgsql*.conf` files contain credentials and are readable.
- The database user can insert into the jail tables.

## Procedure

1. Read `nsswitch.conf` and locate the module configuration.
2. Check permissions on `nss-pgsql.conf` and `nss-pgsql-root.conf`.
3. Connect to PostgreSQL with the found credentials.
4. Insert a user with UID 0 or a privileged GID and authenticate with `su` or SSH.

## Commands

```bash
grep -R nss /etc/nsswitch.conf
ls -l /etc/nss-pgsql*
cat /etc/nss-pgsql-root.conf
psql -h 127.0.0.1 -U <DBUSER> -d <DB>
INSERT INTO passwd_table (username, passwd, uid, gid, homedir) VALUES ('new', '<HASH>', 0, 0, '/root');
```

## Variants

- Use a `sudo` or `wheel` GID instead of UID 0.
- Insert a `shadow_table` entry to control the password.
- Abuse a database user with `UPDATE` on existing rows.

## Limitations

- The module may cache users and take time to reflect changes.
- The database may require a different password than the jail.
- SELinux or AppArmor can stop `su` from querying the module.

## Mitigation

- Restrict access to `nss-pgsql*.conf` and use read-only credentials.
- Separate the database from the jail and audit inserts into `passwd_table`.
- Do not allow UID 0 or privileged GIDs through NSS.

## Detection

- User creation outside the management application.
- `INSERT` queries to NSS tables from an interactive session.
- Logins with UID 0 for newly created users.

## References

- [0xdf — RedCross](https://0xdf.gitlab.io/2019/04/13/htb-redcross.html)
- [GNU libc — Name Service Switch](https://www.gnu.org/software/libc/manual/html_node/Name-Service-Switch.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
