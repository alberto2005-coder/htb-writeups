---
sherlock: Heartbreaker
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, outlook, kape, mft, browser-forensics]
---

# Heartbreaker — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal platform answers.

## Scenario

A KAPE triage of a Windows workstation (`wb-ws-01`) tied to an intrusion is provided. Reconstruct the phishing email, attachment execution, browser activity and possible exfiltration. This is the first Heartbreaker case; do not confuse it with Continuum or Denouement.

## Evidence

- KAPE triage with `$MFT`, EVTX and user artefacts.
- Outlook mailbox in OST/PST format.
- Browser history and downloads (SQLite).
- WinSCP configuration and logs.
- Prefetch, Amcache and startup items.

```bash
sha256sum heartbreaker.zip
unzip -l heartbreaker.zip | head -40
```

Work on a copy and document the time zone. Artefacts may contain credentials; redact them.

## Investigation

### 1. Inventory and triage

Locate the profile and order sources by timeline value:

```text
C/Users/<USER>/NTUSER.DAT
C/Users/<USER>/AppData/Local/Microsoft/Windows/Explorer
C/Users/<USER>/AppData/Roaming/Microsoft/Windows/Recent
C/Windows/System32/winevt/Logs
C/$MFT
```

Parse the OST with `libpff`/`readpst` or a forensic mail tool. Look for executable attachments, macros and URLs.

### 2. Timeline

Cross:

- Email arrival time and attachment name.
- File creation in `Downloads` and Prefetch execution.
- 4688/Sysmon 1 events and network connections.
- Later browsing and downloads.
- WinSCP activity (sessions, hosts, transferred files).

```bash
MFTECmd.exe -f '$MFT' --csv mft.csv
PECmd.exe -d Prefetch --csv prefetch.csv
```

### 3. Key artefact

The chain is confirmed when the attachment name/hash matches the downloaded and executed file, and the first network connection occurs seconds later. WinSCP provides exfiltration evidence if a session to an external host transferred files.

```text
email -> attachment -> Downloads -> Prefetch -> connection -> WinSCP
```

## Findings

- Initial access was an email with a malicious attachment.
- The executable ran from the user profile and connected to a C2.
- Exfiltration used an interactive channel (WinSCP/SFTP) or HTTP.
- IOCs include sender, subject, attachment name/hash, domain/IP and paths.

## Lessons

- The OST keeps the original email and attachment even after deletion.
- Prefetch and MFT show execution; the email shows origin.
- WinSCP stores hosts, users and paths recoverably.
- Correlating three sources avoids blaming a legitimate download.

## References

- <https://mwalkowski.com/post/sherlock-heartbreaker>
- <https://learn.microsoft.com/en-us/outlook/troubleshoot/data-files/ost-file>
- <https://attack.mitre.org/techniques/T1566/001/>
