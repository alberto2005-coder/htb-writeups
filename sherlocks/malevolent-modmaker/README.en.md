---
sherlock: Malevolent ModMaker
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, go, ransomware, discord-webhook, aes-gcm, powershell, reverse-engineering]
---

# Malevolent ModMaker — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

An Acme engineer downloads a mod-making tool from a gaming community. They run it as administrator and their files disappear. Several executables, a note and an encrypted file are provided to reconstruct the chain and recover the content.

## Evidence

- `MCModMaker-v.1.4.exe`, the lure.
- `goteem.exe`, the second stage.
- Ransom note and a file with an anomalous extension.
- Executables are analyzed without running them.

```bash
sha256sum * 2>/dev/null
file *
```

## Investigation

### 1. Inventory and triage

Identify the PEs and hash them before opening. The note and encrypted file extension point to ransomware. `strings` and a Go decompiler show that `goteem.exe` is the second stage.

- `MCModMaker-v.1.4.exe` is the dropper.
- `goteem.exe` is a Go ransomware binary.
- The `.txt` file with the odd extension is the encrypted data.

### 2. Dropper behavior

The lure runs discovery commands (`whoami`, `hostname`, `ipconfig`, `dir`), queries a geolocation service and sends the data to a Discord webhook. It then downloads `goteem.exe` and runs it through PowerShell with `-ep -bypass`.

```text
whoami → hostname → ipconfig → dir → geolocation → webhook → PowerShell → goteem.exe
```

Using a chat webhook as C2 avoids dedicated domains and blends with legitimate traffic.

### 3. Ransomware and encryption

`goteem.exe` walks the filesystem, skips unreadable directories and encrypts text files with AES-GCM. The key is embedded in the binary, so it can be recovered statically.

```text
embedded AES-GCM key → nonce + ciphertext + tag → decrypt without running the malware
```

## Conclusions

- Initial access was social engineering in a gaming community.
- The dropper profiled the host and used Discord as a covert channel.
- The second stage is Go ransomware with an embedded symmetric key.
- Recovery is possible without paying because the key is in the binary.

## Lessons

- Executables shared in communities are not trustworthy.
- Discord webhooks are a C2 channel that is hard to block by domain.
- An embedded key in ransomware enables static recovery.
- Analysis must preserve hashes and chain of custody.

## References

- <https://www.hackthebox.com/sherlocks/Malevolent%20ModMaker>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://attack.mitre.org/techniques/T1102/001/>
- <https://attack.mitre.org/techniques/T1486/>
