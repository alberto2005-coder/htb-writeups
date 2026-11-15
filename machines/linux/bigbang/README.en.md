---
machine: BigBang
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, wordpress, buddyforms, php-filter-chain, cve-2024-2961]
---

# BigBang — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress with BuddyForms allows file reads (CVE-2023-26326); the `wrapwrap` PHP filter chain turns that read into RCE through CVE-2024-2961. WordPress and Grafana hashes allow pivoting, and the Android app leads to root through command injection.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
wpscan --url http://bigbang.htb --enumerate vp,u
curl -s "http://bigbang.htb/wp-admin/admin-ajax.php?action=buddyforms_upload"
php_filter_chain_generator.py --chain '<CHAIN>'
apktool d bigbang.apk
# After access
sudo -l; id
```

## Enumeration

- WordPress and an exposed BuddyForms form.
- Grafana on an internal vhost with reused credentials.
- An Android APK downloadable from the website.

## Initial access

BuddyForms allows path traversal and file reads. Chain it with the glibc `iconv` overflow to build a PHP filter chain that writes a file and executes code as `www-data`.

## Privilege escalation

`wp-config.php` yields database credentials; crack the hashes and reuse them on Grafana. The decompiled APK reveals an endpoint with command injection running as root.

## Evidence

- Read of `wp-config.php` through BuddyForms.
- `wrapwrap` chain and `id` execution.
- Vulnerable APK endpoint and root shell.

## Lessons learned

- File read becomes RCE when charset conversions are chained.
- WordPress secrets are often reused on internal panels.
- A mobile app can expose a weaker API than the website.

## Mitigation and detection

- Update BuddyForms, glibc and PHP.
- Rotate credentials and avoid reuse between WordPress and Grafana.
- Validate and authenticate endpoints used by the mobile app.

## References

- [0xdf — BigBang](https://0xdf.gitlab.io/2025/05/03/htb-bigbang.html)
- [NVD — CVE-2024-2961](https://nvd.nist.gov/vuln/detail/CVE-2024-2961)
- [Hack The Box — BigBang](https://app.hackthebox.com/machines/bigbang)
