---
challenge: Illumination
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, git, base64, secrets-in-history]
---

# Illumination — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The ZIP holds `bot.js`, `config.json` and a **`.git`** directory. The current `config.json` has the token set to "Replace me", but the **git history** contains an earlier version with the real token, base64-encoded. Recover it with `git log` / `git show` and decode.

## Evidence

```text
.
├── bot.js
├── config.json
└── .git/
```

```json
{"token": "Replace me with token when in use! Security Risk!",
 "prefix": "~", "lightNum": "1337",
 "username": "UmVkIEhlcnJpbmcsIHJlYWQgdGhlIEpTIGNhcmVmdWxseQ==", "host": "127.0.0.1"}
```

The `username` is an obvious distractor (it literally says "red herring, read the JS carefully").

## Method

1. **Inspect the history**:

```bash
git log --oneline --all
git log -p --all -- config.json
```

2. **Recover the leaked version**: early in the history the token sat in cleartext in the JSON; a later commit replaced it with the placeholder. `git show <commit>:config.json` returns the original value.

3. **Decode**: the compromised token is base64.

```bash
echo '<token>' | base64 -d
```

4. **Verify** with the bot itself (the `~` prefix reveals which command consumes the token).

## Pitfalls

- **Only reading the current file**: the token is not there anymore; without `.git` there is no challenge.
- **`username`**: a deliberate red herring; it does not lead to the flag.
- **Loose objects**: if `git log` looks empty, `git fsck --lost-found` recovers orphaned commits.

## Lessons

- A published `.git` is a full backup of the code **and** of every secret ever committed.
- Deleting a secret in a later commit does not remove it: rewrite history and rotate the credential.
- A leaked token is compromised even if the service no longer uses it.
