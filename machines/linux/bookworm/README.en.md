---
machine: Bookworm
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, xss, idor, express, symlink, postscript, sqli, privesc]
---

# Bookworm — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

XSS in order notes, avatar upload and an IDOR lead to a ZIP download with traversal that leaks source and database credentials. Those credentials work over SSH for `frank`, who can reach `neil`'s ebook conversion service; a symlink writes an SSH key into his home. As `neil`, `genlabel` runs as root and SQLi injects PostScript into `ps2pdf -dNOSAFER`, allowing a write to `/root/.ssh/authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx redirecting to `bookworm.htb`.
- The app is Express/Node with login, shop, profile and order downloads.
- `feroxbuster` finds `/login`, `/register`, `/shop`, `/profile`, `/basket` and `/static`.

## Enumeration

- The order notes field reflects HTML and allows XSS; CSP does not stop data exfiltration.
- Avatar upload returns a numeric ID and the profile references it without an ownership check (IDOR).
- Downloading multiple books builds a ZIP; a manipulated `bookIds` includes `../../etc/passwd` and `database.js`.

```text
bookIds=1,2,../../../../var/www/bookworm/database.js
```

## Foothold

`database.js` holds the MySQL credentials. The same password works over SSH for `frank`.

```bash
ssh frank@bookworm.htb
```

## Lateral movement

`frank` can read `/home/neil`, where an ebook converter runs on port 3001. The app accepts a file and processes it with Calibre; upload a symlink to `/home/neil/.ssh/authorized_keys` to get a write as `neil`.

```bash
ln -s /home/neil/.ssh/authorized_keys payload
```

## Privilege escalation

`neil` can run `/usr/local/bin/genlabel` as root. The script queries the database and builds a `.ps`; SQLi controls the content and `ps2pdf` runs with `-dNOSAFER`. PostScript allows reading and writing files as root.

```bash
sudo genlabel '99999 UNION SELECT "x) /outfile (/root/.ssh/authorized_keys) (w) file def ...";'
```

You can also read `/root/.ssh/id_ed25519` with `(r) file`.

## Evidence

- XSS, upload and IDOR in the shop.
- ZIP traversal and `database.js`.
- `frank` credentials and `neil`'s service.
- Symlink to `authorized_keys`.
- SQLi/PostScript in `genlabel` and root.

## Lessons learned

- Chaining XSS, upload and IDOR turns minor features into a full leak.
- A ZIP that accepts relative paths is arbitrary read.
- Internal conversion services often write with the user's permissions.
- `ps2pdf` with `-dNOSAFER` turns PostScript into arbitrary read/write.

## Mitigation and detection

- Enforce ownership on every download and normalize paths inside the ZIP.
- Never reuse database credentials for SSH.
- Run converters in a sandbox without `.ssh` access.
- Do not use `-dNOSAFER`; enforce `policy.xml` and review generated `.ps` files.

## References

- [0xdf — Bookworm](https://0xdf.gitlab.io/2024/01/20/htb-bookworm.html)
- [IppSec — Bookworm](https://www.youtube.com/watch?v=UqDdR10F54A)
- [Hack The Box — Bookworm](https://app.hackthebox.com/machines/bookworm)
