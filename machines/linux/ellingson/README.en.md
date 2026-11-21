---
machine: Ellingson
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, flask, werkzeug, debugger, shadow, hashcat, suid, buffer-overflow, rop]
---

# Ellingson — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Flask leaves the Werkzeug debugger reachable on the web. The console executes commands, and since outbound traffic is blocked, it is used to write a public key into `authorized_keys` and log in over SSH as `hal`. `hal` belongs to the `adm` group and can read `shadow.bak`; cracking the hashes yields `margo`'s password. `margo` finds the SUID `/usr/bin/garbage`, a binary with a buffer overflow, no canary and no PIE, but with NX and ASLR. Exploitation is a 64-bit ROP: leak libc, compute offsets and use a `one_gadget` second stage for root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 7.6p1 Ubuntu.
- `80`: nginx 1.14.0 serving a Flask application.

```bash
echo '<IP> ellingson.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://ellingson.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The site has articles and a search box. Triggering an error on an article path shows the Werkzeug debugger page with its insecurity warning. The interactive console is enabled with `__debugger__=yes` and the secret shown on the page; from there, Python commands run on the server.

System enumeration shows the `hal` and `margo` users, and an SSH service. Reverse shell attempts fail, suggesting an outbound firewall.

## Foothold

Since the callback does not work, the debugger writes a public key into `/home/hal/.ssh/authorized_keys`:

```text
__debugger__=yes&cmd=open('/home/hal/.ssh/authorized_keys','a').write('<PUBLIC_KEY>\n')
```

Then SSH as `hal` and remove the added key.

## Lateral movement

`id` shows `hal` is in the `adm` group, with access to logs and backups. Among the files is `shadow.bak`, a copy of the password hashes. It is copied and cracked with `hashcat` or `john`; `margo`'s hash breaks and the password allows `su` or SSH.

```bash
id
find / -group adm -type f 2>/dev/null
cat /var/backups/shadow.bak
hashcat -m 1800 hashes.txt /usr/share/wordlists/rockyou.txt
```

## Privilege escalation

`find / -perm -4000` shows `/usr/bin/garbage`, a non-standard binary that asks for a password. A long input causes a segmentation fault. `checksec` reports:

```text
RELRO: Partial RELRO
Stack: No canary found
NX: NX enabled
PIE: No PIE (0x400000)
```

ASLR is enabled (`/proc/sys/kernel/randomize_va_space` = 2). With no canary and no PIE the return address is controllable, but NX blocks stack execution. The chain is:

1. Measure the offset with `pattern_create`/`pattern_offset`.
2. Use a PLT `puts`/`printf` to leak a libc address.
3. Compute the libc base and the address of `system` or a `one_gadget`.
4. Send a second input with the ROP and get root.

```bash
checksec --file=./garbage
gdb -q ./garbage
pwn checksec ./garbage
ROPgadget --binary ./garbage | grep "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6
```

## Evidence

- Werkzeug debugger page and `id` execution from the console.
- Key added to `authorized_keys` and an SSH session as `hal`.
- `shadow.bak` readable by the `adm` group.
- Cracked `margo` hash and successful `su`.
- `checksec` of the `garbage` SUID and a crash with long input.
- libc leak, second stage and `id` with UID 0.

## Lessons learned

- The Werkzeug debugger must never be reachable in production.
- A `shadow` copy with loose permissions is equivalent to having the passwords.
- A SUID binary without a canary or PIE is still exploitable with NX and ASLR through ROP.
- Leaking a libc address is the missing step to defeat ASLR.
- `adm` and `sudo` group membership must be reviewed during escalation.

## Mitigations and detection

- Disable `debug=True` and the debugger in production; restrict `/console`.
- Protect `shadow`, `shadow.bak` and backups with mode 640 and root ownership.
- Build with `-fstack-protector-strong`, PIE and full RELRO.
- Remove unnecessary SUID bits and audit the remaining ones.
- Alert on `/console` and `__debugger__` access and on SUID binary crashes.
- Monitor reads of `shadow.bak` and changes to `authorized_keys`.

## References

- [0xdf — Ellingson](https://0xdf.gitlab.io/2019/10/19/htb-ellingson.html)
- [IppSec — Ellingson](https://www.youtube.com/watch?v=XVYgBetSvS8)
- [Hack The Box — Ellingson](https://app.hackthebox.com/machines/ellingson)
- [Knowledge — SUID: staged buffer overflow](../../../knowledge/linux/suid-buffer-overflow.en.md)
