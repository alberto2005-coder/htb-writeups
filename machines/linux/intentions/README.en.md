---
machine: Intentions
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, laravel, sqli, imagick, cap-dac-read-search, git]
---

# Intentions — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Laravel gallery allows account registration and stores preferences. A space-stripping filter is bypassed with SQL comments and triggers a second-order injection that leaks bcrypt hashes. The v2 API accepts the hash as a credential, granting administrator access. Imagick image editing yields RCE as `www-data`; Git history leaks `greg`'s password, and `CAP_DAC_READ_SEARCH` on `/opt/scanner/scanner` becomes an MD5 oracle to rebuild root's SSH key.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and Nginx running Laravel.
- `intentions.htb`; a Vue SPA consumes `/api/v1`.
- `feroxbuster` finds `/api`, `/js` and the admin panel.

## Enumeration

- Registration and genre selection store preferences.
- The filter removes literal spaces but not `/**/`.
- Gallery loading concatenates the preference into a query.
- The admin bundle reveals `/api/v2` and the `hash` parameter.

## Foothold

Inject a second-order query in the genres field and recover the users table with bcrypt hashes. The v2 API authenticates by comparing the supplied hash, so the administrator hash is used directly. With an admin session, edit an image and abuse an Imagick pseudo-protocol to run commands.

```bash
sqlmap -r request.txt --second-req feed.txt --batch
```

## Privilege escalation

Review Git history and recover `greg`'s password. `greg` belongs to the `scanner` group and can run `/opt/scanner/scanner`, which has `CAP_DAC_READ_SEARCH`. The binary computes MD5 of files and allows byte comparison; use it as an oracle to reconstruct root's private SSH key byte by byte and log in as root.

```bash
getcap -r / 2>/dev/null
./scanner -p /root/.ssh/id_rsa
```

## Evidence

- API response with bcrypt hashes.
- Admin panel access using the hash.
- `id` as `www-data` from Imagick.
- `getcap` and reconstruction of root's key.

## Lessons learned

- Removing spaces is not a SQLi defense.
- A hash must not be a credential.
- Linux capabilities can turn a read-only binary into an oracle.

## Mitigations and detection

- Use parameterized queries and validate input server-side.
- Never accept hashes as authentication proof.
- Restrict Imagick and capabilities; audit `CAP_DAC_READ_SEARCH`.
- Review Git history before publishing a repository.
- References: HTB Intentions, 0xdf, CWE-89, capabilities(7).

## References

- <https://www.hackthebox.com/machines/Intentions>
- <https://bryanmcnulty.com/posts/htb-intentions>
- <https://cwe.mitre.org/data/definitions/89.html>
- <https://attack.mitre.org/techniques/T1190/>
