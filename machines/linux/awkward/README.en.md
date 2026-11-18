---
machine: Awkward
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, api, jwt, ssrf, file-read, symlink, privesc]
---

# Awkward — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`hat-valley.htb` hosts a store on the `store.hat-valley.htb` vhost. The store portal only checks that the session cookie equals `guest`; changing it to any other value grants access to `/dashboard`. From there, `/api/store-status` takes a URL and requests it from the server (SSRF), while `/api/staff-details` returns users and hashes that are cracked with `hashcat`. The SSRF reaches the internal API documentation, which reveals an `awk` injection that allows file reads and a JWT whose secret is cracked to sign requests. The file read locates a backup, which is downloaded and extracted with `xpad`, and its config yields `bean`'s SSH password. For root the store is abused again: a cart turned into a symlink writes to `leave_requests.csv`, and the mail root processes with that content executes the command injection.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.9p1 Ubuntu 3.
- `80` nginx 1.18.0 (Ubuntu).
- No other open ports.

```bash
ffuf -u http://hat-valley.htb -H "Host: FUZZ.hat-valley.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

The `store.hat-valley.htb` vhost shows up during fuzzing. It is added to `/etc/hosts` alongside the main one.

## Enumeration

The main site is a corporate page linking to the store. `store.hat-valley.htb` requires authentication for `/hr`, but the code only redirects when the session cookie equals `guest`:

```text
Cookie: session=guest  ->  redirect to /hr
Cookie: session=<ANY OTHER VALUE>  ->  /dashboard
```

With the cookie changed the panel loads. The status button issues:

```http
GET /api/store-status?url=%22http://store.hat-valley.htb%22
```

and the response confirms the server fetches the given URL. Pointing it at `http://127.0.0.1:<PORT>` reaches an internal service with the API documentation.

`/api/staff-details` requires no authentication and returns accounts with their hashes:

```bash
curl -s http://hat-valley.htb/api/staff-details | jq -r '.[] | .username + ":" + .password' > hashes
hashcat -m 1400 hashes /usr/share/wordlists/rockyou.txt
```

The cracked passwords allow a login as `christopher.jones`, who has more permissions in the store.

## Foothold

The internal documentation describes an endpoint that runs `awk` with a user-controlled parameter. Escaping the expression achieves command execution and file reads on the server. For routes requiring a JWT, a token is captured and its HMAC secret cracked:

```bash
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
```

With the secret, valid tokens are signed and routes and files are enumerated. The file read locates an application backup, which is downloaded and extracted:

```bash
wget http://hat-valley.htb/<PATH>/backup.tar.gz
tar -xzf backup.tar.gz
```

The archive is password protected. `xpad` (or `john` against the matching format) recovers it, and inside is `bean`'s SSH password:

```bash
ssh bean@hat-valley.htb
```

## Lateral movement

`bean`'s shell is local. Their home holds nothing useful, but they belong to the group that can write to `/var/www/store`, and `/home` contains `christine`'s directory, which receives the application's email. There is no pivot to another network: the next step is escalation on the same host.

## Privilege escalation

Root runs a process that reads `/var/www/private/leave_requests.csv` and sends an email with the leave requests. `bean` cannot write the CSV, but can write the carts directory:

```bash
ln -sf /var/www/private/leave_requests.csv /var/www/store/cart/<UUID>
```

Adding a product to the cart makes the application write to the linked file. A product whose first line holds a command injection is crafted; when root builds the email, the content reaches the command line and executes:

```text
name,surname,date,reason
; <COMMAND> ;
```

The command spawns a root shell. The key point is that the injection does not run in the web app but in the privileged process consuming the CSV.

## Evidence

- Session cookie with a value other than `guest` and access to `/dashboard`.
- SSRF request to `127.0.0.1` returning the internal docs.
- Cracked hashes from `/api/staff-details`.
- Recovered JWT secret and hand-signed token.
- Backup extracted with `xpad` and `bean`'s password.
- Cart symlink to `leave_requests.csv` and a root shell.

## Lessons learned

- Authentication based on a client cookie value authenticates nothing.
- SSRF turns an unexposed internal service into attack surface.
- An `awk` call interpolating user input is a direct path to execution and reads.
- JWTs with weak secrets can be re-signed.
- Asynchronous flows (mail, queues, cron) inherit user data and may run it with more privileges.

## Mitigations and detection

- Validate sessions server-side with an opaque, signed identifier; never trust client values.
- Restrict server-side HTTP egress to an allowlist and block `localhost` and internal ranges.
- Never pass user input to `awk`, `sed` or `sh`; use language APIs and allowlists.
- Sign JWTs with long secrets and rotate them; reject unexpected algorithms.
- Write CSVs with the process's permissions and sanitize content before using it in email.
- Alert on symlinks in upload directories and on mail processes spawning commands.

## References

- [0xdf — Awkward](https://0xdf.gitlab.io/2023/02/25/htb-awkward.html)
- [IppSec — Awkward](https://www.youtube.com/watch?v=gmaizI5Xcqs)
- [Hack The Box — Awkward](https://app.hackthebox.com/machines/awkward)
