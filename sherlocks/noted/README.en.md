---
sherlock: Noted
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, notepad++, extortion, hands-on-keyboard, osint]
---

# Noted — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no platform answers.

## Scenario

Simon, a Forela developer, finds an extortion note on his desktop: someone claims to have collected data from his machine. The CERT only provides the **Notepad++ artifacts**, suspecting the attacker wrote the note and worked from that application with hands-on-keyboard access.

## Evidence

```text
Noted/C/Users/Simon.stark/AppData/Roaming/Notepad++/
├── config.xml
├── session.xml
├── shortcuts.xml
└── backup/
    ├── LootAndPurge.java@2023-07-24_145332
    └── YOU HAVE BEEN HACKED.txt@2023-07-24_150548
```

## Investigation

### 1. File history

`config.xml` keeps the recent-files list in `<File filename="...">` objects. It yields Simon's AWS operations script and his project path:

```bash
grep -o 'filename="[^"]*"' config.xml | sort -u
```

```text
C:\Users\Simon.stark\Documents\Dev_Ops\AWS_objects migration.pl
```

### 2. Backups

`backup/` preserves the content of open documents, even unsaved ones. The file name carries the last-save date and time:

```bash
strings -n 6 "backup/YOU HAVE BEEN HACKED.txt@2023-07-24_150548" | head -40
```

The note demands cryptocurrency and leaves a Tor email address. `session.xml` dates the last modification of the Java code to **2023-07-24 09:53:23 UTC** (NTFS timestamps in the XML), the moment the attacker compiled the tool.

### 3. The attacker's program

`LootAndPurge.java` walks the profile, selects documents and compresses them into `Forela-Dev-Data.zip`, password-protected before exfiltration.

```bash
grep -nE "zip|password|File" "backup/LootAndPurge.java@2023-07-24_145332" | head -20
```

### 4. Contact (OSINT)

The note's address points to an anonymous `.onion` mail provider; the wallet is an **ETH** address. The task is to locate the provider's support address, not to engage the actor.

## Findings

- No malware: the attacker worked **inside Simon's session** (hands-on-keyboard) using his own IDE.
- Target: code and development plans; the AWS script was the map.
- Proof: Notepad++ artifacts give a path and time for every file.

## Lessons

- Desktop applications keep more than users think: recent files, backups and session state.
- `session.xml` and `config.xml` complement each other: the first says what was open, the second what was ever opened.
- A password-protected ZIP built on the host is still exfiltration; the password travels separately.
- Mitigation: purge sensitive histories, keep credentials out of scripts, use a secret manager.
