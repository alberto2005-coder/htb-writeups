---
machine: PermX
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, chamilo, cve-2023-4220, file-upload, setfacl, symlink]
---

# PermX — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Chamilo LMS exposes an unauthenticated upload that allows PHP execution. The configuration leaks database credentials reused by a system user. Privilege escalation abuses a `sudo` script that applies `setfacl` while following a symlink.

## Recon

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH and HTTP.
- The main domain is `permx.htb`.
- Vhost enumeration finds `lms.permx.htb`.

## Enumeration

- `lms.permx.htb` runs Chamilo LMS 1.11.24.
- Admin paths and version details are visible in headers and static resources.
- The upload endpoints and public source for this version are reviewed.

## Foothold

Chamilo is vulnerable to CVE-2023-4220: an unauthenticated upload in `bigUpload.php`.

```bash
curl -s -F "bigUploadFile=@shell.php" \
  "http://lms.permx.htb/main/inc/lib/javascript/bigupload/inc/bigUpload.php?action=post-unsupported"
curl -s "http://lms.permx.htb/main/inc/lib/javascript/bigupload/files/shell.php?cmd=id"
```

The file is reachable under `main/inc/lib/javascript/bigupload/files/`. This yields code execution as the web service account.

## Lateral movement

The Chamilo configuration contains database credentials. The password is reused for the `mtz` account.

```bash
ssh mtz@permx.htb
```

## Privilege escalation

`sudo -l` shows a script that applies ACLs to files in a specific directory:

```bash
sudo -l
sudo /opt/acl.sh <USER> rwx /home/mtz/file
```

The script checks the path prefix, but `setfacl` follows symlinks. A link is created in the allowed path pointing to `/etc/passwd`; the ACL then gives `mtz` write access and allows adding a root user.

## Evidence

- `id` output from the webshell.
- Screenshot of `sudo -l` and the script.
- ACL applied through a symlink.
- Redacted flag.

## Lessons learned

- An unauthenticated upload does not need an obvious endpoint.
- Password reuse turns a configuration leak into SSH access.
- Validating a path prefix is not the same as validating the real file.

## Mitigations and detection

- Update Chamilo and remove the legacy upload.
- Do not reuse service credentials for human accounts.
- Resolve paths with `realpath` and reject symlinks.
- Audit `setfacl` runs from `sudo` and ACL changes on system files.

## References

- <https://www.hackthebox.com/machines/permx>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-4220>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1548/001/>
