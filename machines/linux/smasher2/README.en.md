---
machine: Smasher2
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, dns, pwn, kernel, privesc]
---

# Smasher2 — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`/backup/` provides the source and `ses.so`, a custom session extension. DNS allows AXFR and reveals an internal panel. A refcount bug in `ses.so` bypasses authentication, obtains the API key and reaches command injection in the API; shell-variable obfuscation evades the WAF and yields a `dzonerzy` shell. `/dev/dhid` maps kernel memory and overwrites the `cred` structure to become root.

## Recon

```bash
nmap -Pn -sCV -p22,53,80 <IP>
```

- `22` SSH, `53` DNS and `80` Apache with a login panel.
- `dig axfr smasher2.htb @<IP>` returns `admin.smasher2.htb` and other names.
- `http://<IP>/backup/` lists a ZIP with the source and `ses.so`.

## Enumeration

- The source shows an API at `/api/` that uses `ses.so` to serialize sessions.
- `ses.so` contains a structure with a reference counter and a cleanup function.
- The internal panel exposes `/api/user` and `/api/command`.

## Foothold

Send a crafted session cookie that triggers a double `free` in `ses.so`; the freed object is reused and the authentication check is bypassed. With the admin session, read the API key and call `/api/command`.

```bash
python3 exploit.py --url http://admin.smasher2.htb --cookie '<SESSION>'
```

The API filters `;`, `|` and spaces; concatenate shell variables and use `${IFS}` to run commands.

```bash
curl -s -H 'X-API-KEY: <KEY>' 'http://admin.smasher2.htb/api/command?cmd=a=${PATH:0:1};b=bin;c=sh;$a$b$c'
```

## Lateral movement

The shell is `dzonerzy`. Enumeration shows `/dev/dhid`, a device created by a vulnerable module that allows `mmap` over physical memory.

```bash
ls -l /dev/dhid
dmesg | tail
```

## Privilege escalation

Map `/dev/dhid` into user space and locate the current process's `cred` structure. Writing `uid=0` and `gid=0` into the credentials makes the process root without a SUID binary.

```c
int fd = open("/dev/dhid", O_RDWR);
void *map = mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
// locate cred and overwrite uid/gid
```

## Evidence

- `/backup/` ZIP with `ses.so` and API source.
- AXFR and `admin.smasher2.htb` vhost.
- Crafted cookie and retrieved API key.
- Mapped `/dev/dhid` and `cred` changed to UID 0.

## Lessons learned

- A native session extension can introduce exploitable memory corruption.
- Internal DNS reveals panels that a web scan misses.
- A device mapping physical memory breaks the entire privilege model.

## Mitigation and detection

- Review C extension code and use framework-signed sessions.
- Restrict AXFR and separate internal panels.
- Remove memory-exposing modules and enable SMEP/SMAP/KASLR.

## References

- [0xdf — Smasher2](https://0xdf.gitlab.io/2019/12/14/htb-smasher2.html)
- [IppSec — Smasher2](https://www.youtube.com/watch?v=ELiicja60jI)
- [Hack The Box — Smasher2](https://app.hackthebox.com/machines/smasher2)
