---
topic: Chef knife — Ruby execution through sudo
tags: [linux, chef, knife, ruby, privesc]
---

# Chef knife — Ruby execution through sudo

**English** | [🌐 Español](chef-knife-privesc.md)

## Concept

`knife` is the Chef Infra CLI. Its `exec` subcommand evaluates Ruby in the workstation context; if the user can run it with sudo, they obtain root execution. Another variant opens an editor from `data bag create`, which also allows an escape.

## When it applies

- `sudo -l` shows passwordless `knife` or a broad rule.
- Chef is installed and the binary is accessible.
- A direct escalation from a low-privilege user is needed.

## Procedure

1. Check `sudo -l` and confirm the exact `knife` path.
2. Run `knife exec` with Ruby code that starts a shell.
3. If `exec` is restricted, use `data bag create` to open Vim and escape with `:!/bin/bash`.
4. Verify `id` and read the flag.

## Commands

```bash
sudo -l
sudo knife exec -E "exec '/bin/bash'"
# Editor variant
sudo knife data bag create tmp test -e vim
# Inside Vim: :!/bin/bash
```

## Variants

- `knife node show` with a manipulable `--format`.
- A cookbook or recipe evaluated when `knife` runs.
- A knife plugin writable by the user.

## Limitations

- The sudo rule must allow the specific subcommand.
- Ruby may be restricted by AppArmor or SELinux.
- The Chef version may change the available subcommands.

## Mitigation

- Do not include `knife` in sudo rules; use a wrapper with fixed subcommands.
- Remove the tool from hosts that do not need it.
- Audit plugin and cookbook permissions.

## Detection

- `knife` processes run as root outside a deployment.
- Shells spawned by Ruby or `knife`.
- Interactive `data bag` editor use in production.

## References

- [0xdf — Knife](https://0xdf.gitlab.io/2021/08/28/htb-knife.html)
- [GTFOBins — knife](https://gtfobins.github.io/gtfobins/knife/)
- [Chef — knife exec](https://docs.chef.io/workstation/knife_exec/)
