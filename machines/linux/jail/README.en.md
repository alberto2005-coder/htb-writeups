---
machine: Jail
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, buffer-overflow, nfs, rvim, crypto]
---

# Jail — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port 7411 runs a 32-bit binary with an executable stack and a buffer address leak. An overflow with socket-reuse shellcode gives a shell as `nobody`. NFS with `no_all_squash` allows a SUID binary as `frank`; `rvim` escapes to `adm`, and an encrypted RAR plus a weak RSA key lead to root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
80/tcp    http    Apache 2.4.6 (CentOS)
111/tcp   rpcbind
2049/tcp  nfs
7411/tcp  custom jail service
20048/tcp mountd
```

## Enumeration

- `showmount -e` lists `/opt` and `/var/nfsshare` exported to everyone.
- `/opt` contains the source, the `jail` binary and `compile.sh`.
- The binary is built with `-m32 -z execstack`, so the stack is executable.
- In `DEBUG` mode the service leaks the `userpass` buffer address.

## Foothold

The protocol expects `USER`, `PASS` and optionally `DEBUG`. `DEBUG` leaks the `userpass` address; the offset to EIP is 28 bytes. Socket-reuse shellcode keeps the connection alive and execution jumps to the stack.

```text
USER admin
PASS  <28 bytes> + <addr+32> + <shellcode>
```

The resulting shell is `nobody`.

## Lateral movement

`/etc/exports` uses `root_squash` and `no_all_squash`. A local user with UID 1000 maps to `frank` on the server. A binary calls `setresuid(1000,1000,1000)` and executes `/bin/bash`, is stored in `/var/nfsshare` and marked SUID.

Running it from the `nobody` shell yields `frank`.

```bash
gcc suid.c -o /mnt/nfsshare/suid
chmod 4777 /mnt/nfsshare/suid
```

## Privilege escalation

`frank` may run `rvim` as `adm`. `rvim` restricts `:!` but allows `:python` or `:lua`; either launches a shell and yields `adm`.

`/var/adm` holds a password-policy note, an Atbash-encoded `.frank` file and `keys.rar`. The decoded text hints at an Alcatraz escapee's name and year; a `hashcat` rule generates a wordlist, the RAR is cracked and an RSA public key is extracted.

The key is weak and is factored with `RsaCtfTool`, which rebuilds the private key. It provides SSH access as root.

```bash
sudo -u adm /usr/bin/rvim /var/www/html/jailuser/dev/jail.c
hashcat --stdout -a 3 'Morris?d?d?d?d?s' > words.txt
rar2john keys.rar > keys.hash
john --wordlist=words.txt keys.hash
python3 RsaCtfTool.py --publickey rootauthorizedsshkey.pub --private
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- An executable-stack binary with an address leak is a direct BOF.
- NFS with `no_all_squash` allows UID spoofing and SUID creation.
- `rvim` is not a full jail: `python` and `lua` escape.
- Passwords derived from public trivia are predictable.
- A short or poorly generated RSA key can be factored.

## Mitigations and detection

- Build with NX, ASLR and no address leaks.
- Export NFS with `all_squash` and `root_squash`, and restrict clients.
- Do not allow `rvim` with privileges; use a non-executing editor.
- Use RSA keys of 2048 bits or more with strong passphrases.

## References

- [0xdf — Jail](https://0xdf.gitlab.io/2022/05/23/htb-jail.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+jail+htb)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+jail+writeup)
