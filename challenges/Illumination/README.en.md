---
challenge: Illumination
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, git, history, base64, secrets]
---

# Illumination — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The ZIP ships `bot.js`, `config.json` and the whole **`.git`** directory. The current `config.json` has the token replaced by filler text, but the **history** holds an earlier commit with the real token in base64. `git log` / `git show` recover it and `base64 -d` yields the flag.

## Brief

"A Junior Developer just switched to a new source control platform. Can you find the secret token?" The artifact is the repository itself, not a file dump.

## Recon

```bash
unzip Illumination.zip && cd Illumination.JS
ls -la
git log --oneline --all
git log -p --all -- config.json
```

Layout: `bot.js`, `config.json`, `.git/`. The current `config.json`:

```json
{"token": "Replace me with token when in use! Security Risk!",
 "prefix": "~", "lightNum": "1337",
 "username": "UmVkIEhlcnJpbmcsIHJlYWQgdGhlIEpTIGNhcmVmdWxseQ==",
 "host": "127.0.0.1"}
```

## The flaw

`bot.js` runs `client.login(Buffer.from(config.token, 'base64').toString('ascii'))`: the token is stored base64 and decoded at runtime. The base64 `username` literally says *"Red Herring, read the JS carefully"* — a deliberate distraction.

The history has four commits: the initial one creates the real token, a later one replaces it with the message *"I removed the unique token as it was a security risk"*. Deleting a secret in a later commit does **not** remove it from the repository.

## Exploitation

```bash
git show 47241a4:config.json        # or whichever commit removes it
# "-       "token": "SFRCe3YzcnNpMG5fYzBudHIwbF9hbV9JX3JpZ2h0P30=","
echo 'SFRCe3YzcnNpMG5fYzBudHIwbF9hbV9JX3JpZ2h0P30=' | base64 -d
```

```text
HTB{...}
```

If `git log` looks empty, `git fsck --lost-found` rescues orphaned commits.

## Evidence

```text
.
├── bot.js
├── config.json
└── .git/
```

Trimmed output; the flag is not published.

## Lessons

- **Looking only at the current file**: the token is gone from there; without `.git` there is no challenge.
- **The `username`** is a deliberate red herring; it does not lead to the flag.
- **The "cleanup" commit** is the one that points at where the secret was.

- A published `.git` is a backup of **every** secret ever committed.
- Rotating the token is not enough while the history stays reachable.
- Mitigation: keep `.git` out of artifacts, scan for secrets in CI, rewrite history and rotate credentials.
