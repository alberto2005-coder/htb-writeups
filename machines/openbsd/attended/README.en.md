---
machine: Attended
os: OpenBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [openbsd, smtp, vim, modeline, rop]
---

# Attended — Hack The Box (OpenBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

OpenSMTPD accepts mail from an arbitrary sender and delivers it to `guly`. Opening the message triggers a Vim modeline (CVE-2019-12735) that runs commands. A `.config.swp` reveals `freshness` SSH configuration; from there, a cron and the gateway `authkeys` binary, vulnerable to an overflow, provide ROP and root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh
25/tcp  smtp   OpenSMTPD
80/tcp  http   nginx
```

## Enumeration

- Port 25 accepts `MAIL FROM` and `RCPT TO` for local users.
- Delivery to `guly` works even when the sender does not exist.
- Mail is processed with Vim/Neovim and a modeline can execute commands.
- Local enumeration shows a `.config.swp` with SSH configuration.

## Foothold

A mail with a malicious modeline is sent. When opened, Vim interprets `:!` and runs a reverse shell as `guly`.

```bash
swaks --to guly@attended.htb --from freshness@attended.htb   --header 'Subject: hello' --body 'see attached'   --attach-type text/plain --attach @payload.txt --server <IP>
```

The payload uses `modeline` and `assert_fails()` to run the command without interaction.

## Lateral movement

In `guly`'s home, a `.config.swp` retains SSH configuration: `User freshness`, `ControlMaster` and the socket path. With that information and the available key/agent, SSH opens as `freshness`.

```bash
strings ~/.config.swp
ssh freshness@attended.htb
```

## Privilege escalation

`freshness` runs an `fchecker.py` cron that processes files in `/home/shared` and calls `ssh -F <file>`. A controlled file can include SSH options and run a local command.

The next hop is the gateway: `/home/freshness/authkeys` is an OpenBSD ELF executed by `sshd` as root and overflows its stack while parsing a large RSA key. A ROP chain calls `execve("/usr/local/bin/python2", ...)` and yields root on `attendedgw`.

```bash
cat /home/freshness/note.txt
file /home/freshness/authkeys
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A mail server accepting arbitrary senders enables internal phishing.
- Vim modelines are code execution when a file is opened.
- Vim swap files leak configuration and paths.
- A binary executed by `sshd` as root is a critical surface.

## Mitigations and detection

- Require authentication and validate senders in OpenSMTPD.
- Disable `modeline` or use `securemodelines`.
- Clean swap files and protect shared directories.
- Build `authkeys` with mitigations and validate key sizes.

## References

- [0xdf — Attended](https://0xdf.gitlab.io/2021/05/08/htb-attended.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+attended)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+attended+writeup)
