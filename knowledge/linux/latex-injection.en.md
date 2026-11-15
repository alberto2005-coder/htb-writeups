---
topic: LaTeX injection
tags: [linux, latex, file-read, command-injection]
---

# LaTeX injection

[🌐 Español](latex-injection.md) | **English**

## Concept

A service compiling LaTeX with user input may allow file reads through `\input` or `\lstinputlisting`. If `shell-escape` is enabled, commands can also run through `\write18`.

## When it applies

- The application compiles LaTeX or renders formulas.
- Input is not restricted to math.
- The engine can access host files.

## Procedure

1. Try `\input{/etc/passwd}`.
2. Use `\lstinputlisting` for files with special characters.
3. Read configuration and credentials.
4. Try `\write18` if `shell-escape` is enabled.

```latex
\input{/etc/passwd}
\lstinputlisting{/var/www/dev/.htpasswd}
\immediate\write18{id}
```

## Variants

- Read SSH keys or application configuration.
- Write a file with `\newwrite`.
- Combine with LFI to reach the engine.

## Limitations

- The engine must allow the primitives.
- The path must be readable.
- `shell-escape` is usually disabled.

## Mitigation and detection

- Run LaTeX in a sandbox without files.
- Disable `shell-escape` and limit packages.
- Validate input as math.

## References

- <https://latex-project.org/>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
