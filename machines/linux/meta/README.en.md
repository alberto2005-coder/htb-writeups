---
machine: Meta
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, exiftool, cve-2021-22204, command-injection, cron, pspy]
---

# Meta — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A vhost accepts images and uses ExifTool to process metadata. The version is vulnerable to CVE-2021-22204 and allows command execution when parsing a malicious DjVu. Job enumeration reveals an editable cron that leads to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Enumerate vhosts with `ffuf`/`wfuzz`; add the management subdomain to hosts. The application allows image upload and displays metadata.

## Initial access

Identify the vulnerable ExifTool version. Create a DjVu image with a payload in its metadata:

```bash
exiftool -config exploit.config image.jpg
```

Uploading and processing it executes the command. This returns a shell as the service user.

## Lateral movement

```bash
pspy64
```

A cron runs a user-owned script. Modify it to launch a reverse shell as the account running the job.

## Privilege escalation

Repeat process and job enumeration. Find another root-run script or binary with weak permissions, or a misconfigured `sudo` rule. Inject a command and get root.

## Evidence

- ExifTool version and DjVu file.
- Upload request and shell.
- `pspy` output.
- Modified script and root shell.

## Lessons learned

- Image metadata is an attack surface.
- Old ExifTool enables execution while parsing DjVu.
- `pspy` discovers jobs without `crontab` access.
- Weakly permissioned cron scripts mean escalation.

## Mitigation and detection

- Update ExifTool and validate images.
- Process uploads in a networkless sandbox.
- Restrict write access to cron scripts.
- Monitor child processes of `exiftool` and cron.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-22204>
- <https://www.hackthebox.com/machines/meta>
- <https://github.com/DominicBreuker/pspy>
