---
topic: Bypass de WAF en inyección de comandos
tags: [web, waf, command-injection, bypass, lua]
---

# Bypass de WAF en inyección de comandos

**English** | [🇪🇸 Español](waf-command-injection-bypass.md)

## Concept

A WAF filters characters or keywords, but the application still concatenates input into a shell command. Equivalent syntax (quotes, variables, wildcards, encoding) executes commands without the blocked tokens.

## When it applies

- Parameters reaching `system`, `popen`, `exec` or `bash -c`.
- WAFs with blacklists for `;`, `|`, `$`, `(`, `)`.
- Filters inspecting only the User-Agent or decoded URL.

## Procedure

1. Confirm injection with a harmless expression.
2. Identify blocked characters and the quoting context.
3. Break the context with single quotes and split words with `''`.
4. Send a raw request if the client normalizes the URL.

```bash
curl "http://<HOST>/sync?opt=' id'"
curl "http://<HOST>/sync?opt=' c''at /etc/passwd'"
# Alternatives: ${IFS}, wildcards, variables, double encoding
curl --path-as-is "http://<HOST>/sync?opt='%20id'"
```

## Variants

- `$IFS` or `${IFS}` for spaces.
- `?`, `*` and wildcards for paths.
- Environment variables and indirect expansion.
- Unicode or double URL encoding.

## Limitations

- The WAF may normalize and decode before matching.
- The quoting context must be exploitable.
- Raw requests may need a client that does not normalize.

## Mitigation and detection

- Do not build shell commands from external input; use argument-array APIs.
- Enforce allowlists in code, not only at the WAF.
- Log and alert on injection patterns and anomalous child processes.

## References

- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://portswigger.net/web-security/os-command-injection>
- <https://attack.mitre.org/techniques/T1059/004/>
