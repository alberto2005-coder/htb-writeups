---
topic: Vim — execution through modelines
tags: [linux, vim, modeline, rce, editor]
---

# Vim — execution through modelines

[🌐 Español](vim-modeline-rce.md) | **English**

## Concept

Vim can apply options declared in the first or last lines of a file (`modeline`). If `modelineexpr` is enabled, an expression such as `foldexpr` or `statusline` can run commands when the file is opened.

## When it applies

- A victim opening a file in Vim with `modeline` enabled.
- `modelineexpr` or older vulnerable versions.
- Editors used by root or by a service.

## Procedure

1. Check `:set modeline?` and `:set modelineexpr?`.
2. Create a file with a malicious modeline.
3. Get the victim to open it in Vim.
4. Verify execution with a test file.
5. Escalate if the editor runs as root.

## Commands

```vim
" Test modeline
vim: set foldmethod=expr foldexpr=system('id'):
```

## Variants

- `statusline` with `%{system('id')}`.
- `errorformat` or `makeprg`.
- Opening the file from `git`, `less` or an integrated editor.

## Limitations

- `modeline` may be disabled.
- `modelineexpr` only exists in recent versions.
- The file must be opened with Vim, not `cat`.

## Mitigation

- Disable `modeline` and `modelineexpr` on sensitive systems.
- Do not open untrusted files as root.
- Patch Vim.

## Detection

- Files with unusual `vim:` or `ex:` lines.
- Child processes of Vim running commands.

## References

- <https://vimhelp.org/options.txt.html#%27modeline%27>
- <https://attack.mitre.org/techniques/T1059/>
