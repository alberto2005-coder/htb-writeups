---
topic: Command injection
tags: [web, command-injection, rce, blind, commix, shell]
---

# Command injection

**English** | [🇪🇸 Español](command-injection.md)

## Concept

Command injection occurs when an application passes user input to a shell without separating arguments or validating characters. It can be direct, when output is reflected, or blind, when only timing, errors or side effects are observable.

## When it applies

- Parameters used in `ping`, `nslookup`, `convert` or scripts.
- Forms that run system utilities.
- Responses containing command output.
- Functions that allow delays or file writes.

## Procedure

1. Identify the parameter and underlying command.
2. Test separators and substitutions.
3. Confirm with a harmless command.
4. Use time or DNS for blind cases.
5. Stabilise execution or the reverse shell.

```bash
curl -s 'http://<HOST>/ping?ip=127.0.0.1;id'
curl -s 'http://<HOST>/ping?ip=127.0.0.1%0aid'
curl -s 'http://<HOST>/ping?ip=127.0.0.1;sleep+5'
commix --url='http://<HOST>/ping?ip=127.0.0.1' --os-cmd=id
```

## Variants

- Separators `;`, `|`, `||`, `&&`, `$()` and backticks.
- Blind injection through time or DNS.
- Filters blocking spaces or keywords.
- Injection into image or PDF tool arguments.

## Limitations

- The command may run inside a container.
- Filters may block characters.
- Output may not be reflected.
- The process may have few privileges.

## Mitigation and detection

- Avoid shells and use APIs with separate arguments.
- Validate with allowlists and escape.
- Run with minimal privileges and no network.
- Alert on child processes, `sh -c` and separator patterns.

## References

- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
- <https://github.com/commixproject/commix>
