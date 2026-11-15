---
machine: Faculty
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, mpdf, meta-git, gdb, ptrace]
---

# Faculty — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLi in the school login grants administrator access. An mPDF feature reads files and exposes the database password, reused by a local user. `meta-git` provides command injection and that user GDB has `CAP_SYS_PTRACE`, enough to inject into a root process.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
# Login SQLi
sqlmap --url "http://faculty.htb/login.php" --data="username=admin&password=x" --batch
# mPDF file read
curl -s "http://faculty.htb/pdf.php?template=../../../../etc/passwd"
# meta-git
meta-git clone 'git@github.com:x/y.git; id'
# GDB with capability
getcap $(which gdb)
gdb -p <ROOT_PID> -ex "call system(\"id\")" -ex quit
```

## Enumeration

- School application with login and PDF generation.
- mPDF reachable through a template or file parameter.
- User with `meta-git` and GDB holding `cap_sys_ptrace`.

## Initial access

Bypass the login with SQLi and reach the panel. The PDF feature accepts a path and mPDF resolves it, allowing file reads; the database configuration contains a password reused over SSH.

## Privilege escalation

With the local account, run `meta-git`, which passes arguments to Git unsanitized; inject a command to pivot to another user. That user can run GDB with `cap_sys_ptrace`; attach to a root process and run `call system`.

## Evidence

- Login bypass with SQLi.
- File read through mPDF and SSH password.
- meta-git injection and `call system` from GDB.

## Lessons learned

- PDF libraries can read files when they accept paths.
- Reused database credentials widen access.
- A ptrace capability equals execution in other processes.

## Mitigation and detection

- Parameterize queries and restrict PDF templates.
- Do not reuse passwords across services.
- Remove `cap_sys_ptrace` from GDB and restrict `meta-git`.

## References

- [0xdf — Faculty](https://0xdf.gitlab.io/2022/10/22/htb-faculty.html)
- [mPDF — Documentation](https://mpdf.github.io/)
- [Hack The Box — Faculty](https://app.hackthebox.com/machines/faculty)
