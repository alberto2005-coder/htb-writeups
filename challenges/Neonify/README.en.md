---
challenge: Neonify
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ssti, crlf, regex-bypass, ruby]
---

# Neonify — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app "neonifies" text with a template and filters keywords with a weak regex. A newline/CRLF and an SSTI expression execute code and read the flag.

## Prompt and surface

- Web, Easy, retired.
- Text transformation form.
- Regex filter.

```bash
curl -i http://<HOST>/
```

## Reconnaissance

Test an arithmetic expression and see if it is evaluated. Review blocked characters and the template engine (Ruby/ERB).

```text
<%= 7*7 %>
```

## Analysis

1. Identify the filter and look for a bypass with `%0a`, casing or concatenation.
2. Confirm SSTI.
3. Execute a system command.
4. Read the flag.
5. Redact the output.

```text
<%= system('cat /flag*') %>
```

## Root cause

The regex does not cover newlines or syntax variants, and input is evaluated in the template. The filter is an incomplete blacklist.

## Local reproduction

1. Run the ERB app.
2. Test the expression.
3. Apply the CRLF bypass.
4. Run `id`.
5. Fix the filter and compare.

## Evidence

- Request with the bypass.
- Command output.
- Redacted flag.

## Lessons learned

- Blacklist regexes are fragile.
- CRLF can break validation.
- ERB evaluates Ruby code.
- Template context matters.

## Mitigation and detection

- Never evaluate input as a template.
- Use safe rendering and escaping.
- Character allowlist.
- Monitor web-server child processes.

## References

- <https://www.hackthebox.com/challenges/neonify>
- <https://owasp.org/www-community/attacks/Server_Side_Template_Injection>
- <https://www.ruby-lang.org/en/documentation/>
