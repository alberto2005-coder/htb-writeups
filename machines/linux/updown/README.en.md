---
machine: UpDown
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ssrf, git-dumper, vhosts, sudo, apt]
---

# UpDown — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A website checks whether a URL responds and is vulnerable to SSRF. Source code exposed in a Git repository reveals an internal virtual host and an execution path. The obtained credentials provide SSH; a `sudo` rule on a package-management tool provides root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://<IP> -H 'Host: FUZZ.updown.htb' -w <WORDLIST>
```

- SSH and Apache.
- The main application checks a URL's status.
- Virtual hosts and an accessible Git repository exist.

## Enumeration

- `/.git/` exists and can be extracted with `git-dumper`.
- The code shows a server-side HTTP request and an allowlist.
- The development vhost reveals credentials or an admin path.
- SSH access uses a user with a specific `sudo` rule.

## Foothold

Use the status checker to request an internal resource and confirm SSRF. The source reveals parameters and hidden paths; credentials from the vhost provide SSH.

```bash
git-dumper http://<IP>/.git/ ./src
curl -s 'http://<IP>/check' --data-urlencode 'url=http://127.0.0.1:80/'
```

## Privilege escalation

`sudo -l` shows a package-management binary or script with an option that runs a command. Prepare a local package/file and invoke the rule without changing anything outside the lab.

```bash
sudo -l
sudo <BINARY> --help
```

## Evidence

- Server response to an internal URL.
- Extracted Git repository and vulnerable code.
- SSH session as the discovered user.
- Controlled `sudo` execution and root.

## Lessons

- A URL checker can become SSRF.
- An exposed `.git` leaks code, paths and credentials.
- Internal virtual hosts must not trust the main host's filtering.
- `sudo` rules on package managers are dangerous.

## Mitigations and detection

- Block internal schemes and ranges in the checker.
- Do not publish `.git`, backups or development environments.
- Audit `sudo -l` and restrict options that execute commands.
- Alert on requests to `127.0.0.1` and repository downloads.
- References: OWASP SSRF, GTFOBins, HTB UpDown.

## References

- <https://www.hackthebox.com/machines/UpDown>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://gtfobins.github.io/>
- <https://attack.mitre.org/techniques/T1552/>
