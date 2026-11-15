---
machine: Dog
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, backdrop-cms, git, module-upload, bee, privesc]
---

# Dog — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed `.git` repository in Backdrop CMS leaks `settings.php` and database credentials. With the `tiffany` account, upload a malicious module to get `www-data`; a shared password moves to `johncusack`. That user can run `bee` as root, and `bee eval` runs arbitrary PHP, including a root shell.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with Backdrop CMS.
- `nmap` detects `http-git` and `feroxbuster` confirms `/.git/`.
- `robots.txt` lists admin paths.

## Enumeration

`git-dumper` rebuilds the repository. `settings.php` contains the MySQL connection string and `tiffany` appears in the configuration.

```bash
git-dumper http://dog.htb/.git dog-src
grep -R "mysql://" dog-src
```

## Foothold

Log in as `tiffany`, open the Backdrop panel and upload a malicious module. The module includes a PHP webshell that runs when visited and gives `www-data`.

```bash
curl 'http://dog.htb/modules/<MODULE>/shell.php?cmd=id'
```

## Lateral movement

The database password also works for `johncusack` on the system.

```bash
su johncusack
```

## Privilege escalation

`johncusack` can run `bee` as root. `bee eval` evaluates PHP in the installation context; `system("bash")` returns a root shell.

```bash
sudo bee eval 'system("bash")'
```

## Evidence

- Exposed `.git` and `settings.php`.
- `tiffany` credentials.
- Malicious module and `www-data`.
- Shared password and `johncusack`.
- `bee eval` and root.

## Lessons learned

- An exposed `.git` leaks configuration and credentials.
- CMS module upload is executable code.
- Database passwords are reused far too often.
- An admin tool with `eval` is execution as its user.

## Mitigation and detection

- Never publish `.git`; rotate credentials if exposed.
- Validate and sign modules; restrict upload to administrators.
- Separate database and system passwords.
- Do not allow `bee eval` as root; use a wrapper with allowed commands.

## References

- [0xdf — Dog](https://0xdf.gitlab.io/2025/07/12/htb-dog.html)
- [IppSec — Dog](https://www.youtube.com/watch?v=Z24FN8qqngY)
- [Hack The Box — Dog](https://app.hackthebox.com/machines/dog)
