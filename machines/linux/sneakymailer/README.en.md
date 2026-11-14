---
machine: SneakyMailer
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, smtp, phishing, imap, ftp, pypi, sudo]
---

# SneakyMailer — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site exposes employee emails and SMTP accepts messages. A user clicks a phishing link and submits credentials; their IMAP mailbox reveals FTP access. FTP upload drops a webshell; an internal PyPI server executes code during package installation and `sudo pip` provides root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p21,22,25,80,143,993,8080 <IP>
```

- FTP, SSH, SMTP, HTTP, IMAP and a PyPI server.
- The site has a team page with email addresses.
- SMTP accepts connections and allows user probing.

## Enumeration

- Collect emails and test a phishing link with a controlled form.
- A user visits the URL and submits credentials to the attacker server.
- The IMAP mailbox contains FTP credentials.
- FTP writes to the development vhost directory.

## Foothold

Send an email with the form link, capture the request and access IMAP. Use the FTP credentials to upload PHP to the vhost and execute it.

```bash
swaks --to <USER> --server <IP> --body 'http://<ATTACKER>/'
curl -u <USER>:<PASS> ftp://<IP>/
```

## Privilege escalation

The internal PyPI server installs user packages. Publish a package whose `setup.py` runs a command; installation happens as another user. The `sudo pip` rule repeats execution as root.

```bash
python3 -m build
twine upload --repository-url http://pypi.sneakycorp.htb:8080/ dist/*
sudo -l
```

## Evidence

- Email sent and credentials captured.
- IMAP access and FTP credentials.
- Webshell on the vhost.
- PyPI package executed and root through `sudo pip`.

## Lessons

- Email and phishing are an initial-access surface.
- A mailbox can contain credentials for other services.
- Internal package indexes execute code on install.
- `sudo pip` is equivalent to root execution.

## Mitigations and detection

- Train users and enforce DMARC/SPF; filter links.
- Do not reuse credentials across mail, FTP and applications.
- Sign packages and restrict who can publish to the internal index.
- Avoid `sudo pip`; use virtual environments and least privilege.
- References: OWASP Phishing, PyPI security, HTB SneakyMailer.

## References

- <https://www.hackthebox.com/machines/SneakyMailer>
- <https://owasp.org/www-community/attacks/Phishing>
- <https://attack.mitre.org/techniques/T1566/>
- <https://attack.mitre.org/techniques/T1546/>
