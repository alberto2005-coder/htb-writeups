---
machine: Editorial
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, git, gitpython, cve-2022-24439, privesc]
---

# Editorial — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The cover upload downloads a URL and stores the response, allowing SSRF against a localhost API. The API leaks `dev` SSH credentials; a Git repository in dev's home has an old revision with `prod`'s password. `prod` can run a script using GitPython 3.1.29, vulnerable to CVE-2022-24439, and the `ext::` argument gives root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` nginx with a publishing site.
- Cover upload accepts a URL and stores a preview in `/static/uploads/<uuid>`.
- The site resolves `editorial.htb`.

## Enumeration

Point the URL at the host and at `localhost` on different ports. Port fuzzing with `ffuf` finds an internal API on `5000`. Fetch the response from the static file; `/api/latest/metadata/messages/authors` contains a welcome message with a username and password.

## Foothold

`dev` credentials work over SSH. `~/apps` has a `.git` without the working files; `git log` and `git diff` between commits show the change from `prod`'s password to `dev`'s, revealing `prod`'s.

```bash
# SSRF to the internal API
url=http://localhost:5000/api/latest/metadata/messages/authors
# CVE-2022-24439
sudo /usr/bin/python3 /opt/.../clone_prod_change.py 'ext::sh -c /dev/shm/root.sh'```

## Lateral movement

`prod`'s password works over SSH. `prod` can run `/opt/.../clone_prod_change.py` as root, which calls `Repo.clone_from(sys.argv[1], ...)`.

## Privilege escalation

GitPython 3.1.29 is vulnerable to CVE-2022-24439: passing an `ext::sh -c <command>` URL makes Git run the command with `protocol.ext.allow=always`. Point it at a writable script that copies bash and sets SUID, then run it with sudo.

## Evidence

- SSRF to `localhost:5000`.
- `dev` credentials from the API.
- `git diff` with `prod`'s password.
- GitPython 3.1.29 and `ext::` as root.

## Lessons learned

- A URL fetch can reach internal services.
- Git repositories retain secrets even after files are deleted.
- Old GitPython dependencies allow argument injection.
- A sudo script accepting a URL is a trust boundary.

## Mitigation and detection

- Validate destinations and block loopback in fetches.
- Rotate secrets and purge Git history.
- Update GitPython and disable `protocol.ext`.
- Do not run clones as root.

## References

- [0xdf — Editorial](https://0xdf.gitlab.io/2024/10/19/htb-editorial.html)
- [IppSec — Editorial](https://www.youtube.com/watch?v=eggi_GQo9fk)
- [Hack The Box — Editorial](https://app.hackthebox.com/machines/editorial)
