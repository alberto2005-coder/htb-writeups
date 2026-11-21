---
machine: Moderators
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, upload-bypass, wordpress, virtualbox, luks, hashcat, privesc]
---

# Moderators — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A `report` parameter in `reports.php` enumerates reports by ID; walking the IDs reaches the upload page. The filter requires a PDF, but it is bypassed by changing the MIME type, the magic bytes and the name to `htb.pdf.php`; `popen` (not disabled) provides a shell as `www-data`. An internal WordPress runs on localhost: the Brandfolder plugin moves to `lexi`, and `wp-config.php` yields the MySQL password. Another database holds secrets encrypted by the passwords-manager plugin; source analysis decrypts them and reveals `john`'s SSH key. His home has a VirtualBox VM (`2019.vdi`) with disk encryption and LUKS; breaking both layers yields a password that works for `sudo`, and `john` has `(root) ALL`.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: Apache httpd 2.4.41.

```bash
echo '<IP> moderators.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://moderators.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The site has reports at `reports.php?report=<ID>`. `wfuzz` walks the IDs and finds the upload page; the internal WordPress appears later, from the shell.

Local port enumeration shows web and database services unreachable from outside; a tunnel is used to reach them.

## Foothold

The upload page requires a PDF and validates MIME type, magic bytes and extension. The request sends `Content-Type: application/pdf`, prepends `%PDF-` to the content and uses the name `htb.pdf.php`; that passes the filter and the server executes the final `.php`. The webshell runs, although `disable_functions` blocks `system`, `exec`, `shell_exec` and `passthru`; `popen` is not blocked, so it launches the reverse shell and provides a shell as `www-data`.

## Lateral movement

An internal WordPress (`site.new`) runs on localhost. The Brandfolder plugin has a vulnerability that reads files or performs actions with the site's privileges; it is exploited to gain access as `lexi`. Her group grants access to `wp-config.php`, with the MySQL credentials.

MySQL exposes the WordPress database and the passwords-manager plugin secrets. The plugin code shows the encryption and key; records are decrypted and `john`'s SSH key appears. SSH logs in as `john`.

## Privilege escalation

`john` has scripts and a VirtualBox VM in his home: `2019.vdi` and `2019-08-01.vbox`. The disk is encrypted by VirtualBox and, inside, by LUKS. The encrypted material is extracted and the VirtualBox password is cracked with `pyvboxdie-cracker` (or with the hash produced by `virtualbox2hashcat.py`). For LUKS, Hashcat does not support LUKS2 in that version, so the passphrase is tested locally with `cryptsetup luksOpen --test-passphrase`. The resulting password works for `sudo`.

```bash
python3 pyvboxdie-cracker.py -v 2019-08-01.vbox -d /usr/share/wordlists/rockyou.txt
sudo -l
sudo -i
```

`sudo -l` confirms `(root) ALL` for `john`, so `sudo -i` completes the box.

## Evidence

- Report enumeration by ID and discovery of the upload page.
- `htb.pdf.php` webshell executed despite the filter and `disable_functions`.
- Internal WordPress and Brandfolder plugin.
- `wp-config.php` with MySQL credentials.
- Decrypted passwords-manager secrets and `john`'s SSH key.
- VDI with VirtualBox encryption and LUKS broken.
- `sudo -l` with `(root) ALL` and `id` with UID 0.

## Lessons learned

- A report IDOR maps the application and exposes internal functions.
- Blocklist-based upload filters are bypassed.
- `disable_functions` is not isolation; execution paths remain.
- WordPress plugins and their databases accumulate secrets.
- A development VM can hold production credentials.
- VirtualBox and LUKS can be broken when the password is weak.

## Mitigations and detection

- Do not use user-controlled filenames; map IDs to paths.
- Validate uploads by content and allowed extension, and store outside the webroot.
- Combine `disable_functions` with `open_basedir` and an unprivileged user.
- Audit WordPress plugins and credentials; rotate MySQL passwords.
- Do not store VMs with credentials in user homes.
- Use strong VirtualBox and LUKS passwords; monitor `sudo` and mounts.

## References

- [0xdf — Moderators](https://0xdf.gitlab.io/2022/11/05/htb-moderators.html)
- [IppSec — Moderators](https://www.youtube.com/watch?v=V70gFSoh3aU)
- [Hack The Box — Moderators](https://app.hackthebox.com/machines/moderators)
- [Knowledge — VirtualBox, VDI and LUKS](../../../knowledge/forensics/virtualbox-vdi-luks.en.md)
