---
sherlock: Noted
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, notepad++, extortion, osint, aws, windows]
---

# Noted — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

Simon, a developer at Forela, found an extortion note on his desktop: someone claims to have collected sensitive data from his machine. The CERT hands over only the **Notepad++ artefacts**, suspecting the attacker wrote the note and staged everything from there. There is an **OSINT** component: contact the actor using third-party services.

## Evidence

```text
%APPDATA%\Notepad++\config.xml
%APPDATA%\Notepad++\backup\
%APPDATA%\Notepad++\session.xml
%APPDATA%\Notepad++\shortcuts.xml
```

## Investigation

### 1. File history

`config.xml` keeps recent files as `File` objects with `filename`, `path` and `encoding` attributes. That yields the paths of scripts Simon worked with and, above all, the files the attacker opened.

```bash
grep -o 'filename="[^"]*"' config.xml | sort -u
grep -o 'path="[^"]*"' config.xml | sort -u
```

Look for an AWS operations script (name and full path): it is the usual first question in this case and the hint that the attacker wanted credentials.

### 2. Backups

Notepad++ drops open documents, even unsaved ones, into `backup\`:

```bash
ls -la backup/
file backup/*
strings -n 6 backup/* | head -60
```

The extortion note text, the contact link and possibly content Simon never saved show up here.

### 3. Session and tabs

`session.xml` lists documents open at shutdown with their paths; it orders what was opened before and after, and flags files that no longer exist (deleted by the attacker).

### 4. Contact OSINT

The note's contact address (anonymous mail service or `.onion`) is resolved through public services. Document the provider and creation date if visible; do not engage the actor beyond what the challenge requires.

## Findings

- Access: the attacker worked **in Simon's own session** (hands-on-keyboard), not through automated malware.
- Goal: AWS scripts and credentials, then the extortion note.
- Key proof: the Notepad++ history dates and locates every action.

## Lessons

- Desktop applications store far more than users think: recents, backups and session data.
- Hands-on-keyboard is proven with application artefacts, not with a binary's `Prefetch`.
- Mitigation: purge sensitive histories, never hardcode credentials in scripts, and use a secrets manager.
