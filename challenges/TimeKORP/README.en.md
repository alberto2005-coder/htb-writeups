---
challenge: TimeKORP
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, command-injection, php, cyber-apocalypse-2024]
---

# TimeKORP — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A web app renders the time using a **format** taken from a parameter. The server builds a **shell command** with that value unsanitised: add `;` and anything runs. The challenge ships the source, so the flaw is plain to see.

## Evidence

- A web instance and, depending on the version, the app's PHP source.

## Method

1. **Spot the parameter**: a URL such as `?format=%H:%M` returns the formatted time.

2. **Read the source** when available; it looks like

```php
$format = $_GET['format'] ?? 'H:i:s';
return shell_exec("date +'$format'");
```

3. **Inject**: close the quote and chain.

```text
?format=';cat /flag;'
?format=';id;'
```

4. **Variants** when filtered: `$(cat /flag)`, backticks, or `%0a` for a newline.

5. **Alternative**: a leaked `Dockerfile` reveals the real flag path.

## Pitfalls

- **URL encoding**: `;` and spaces may need `%3B`, `%20` depending on the client.
- **Quotes**: if the value is interpolated inside single quotes, close them before the `;`.
- **Empty output**: try `id` or `whoami` before assuming there is no injection.

## Lessons

- Interpolating user input into a shell command is command injection, even for "just" a date format.
- Source code in the challenge removes the guessing phase.
- `escapeshellarg` and an allowlist of formats are the fix.
