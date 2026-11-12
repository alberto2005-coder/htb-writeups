---
sherlock: OpTinselTrace-1
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, insider, em-client, jumplists, mft]
---

# OpTinselTrace-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

“Elfin” works odd hours and appears to bypass controls. Santa's intelligence suspects an insider. A KAPE triage of the workstation and a live-response capture are provided; audit the user's activity, email and files they may have sent.

## Evidence

- `TriageData`: `$MFT`, USN Journal, registry, EVTX, profiles and application artefacts.
- `LiveResponse`: processes, connections and system state at collection time.
- `eM Client` mail client under `AppData\Roaming`.
- Jump lists, `RecentDocs` and MFT/USN.

```bash
sha256sum optinseltrace-1.zip
unzip -l optinseltrace-1.zip | head -30
```

## Investigation

### 1. Inventory and triage

The live capture identifies the mail client and its process:

```text
LiveResponse/pstree.txt
LiveResponse/netstat.txt
TriageData/Users/<USER>/AppData/Roaming/eM Client
```

`pstree` shows `MailClient.exe` under `explorer.exe`, confirming the user opened it. The `eM Client` folder holds accounts, folders and attachments.

### 2. Timeline

Cross:

- `eM Client` launch and last activity.
- Sent/received mail and attachments.
- Binary and ZIP creation on disk.
- Jump lists and `RecentDocs` for the exact path.
- USN/MFT for creation time.

```bash
MFTECmd.exe -f '$MFT' --csv mft.csv
JLECmd.exe -d AutomaticDestinations --csv jl.csv
```

### 3. Key artefact

The sent email contains a compressed binary (`santa_deliveries.zip`) with hardcoded credentials and logic to query an S3 bucket. Jump lists and `$MFT` give creation time and the folder where it was prepared. Analyse the binary with `strings` and a decompiler.

```text
eM Client -> email -> ZIP attachment -> binary -> credentials/S3
```

## Findings

- Elfin used the mail client to send a sensitive binary to a third party.
- The ZIP was created in a profile folder and attached to the email.
- The binary contains credentials and S3 access.
- IOCs are the email account, ZIP name, binary hash and bucket.

## Lessons

- `eM Client` stores accounts and messages under `AppData\Roaming`.
- Jump lists provide path and creation time.
- MFT/USN confirm the sequence even if the email is deleted.
- An insider can exfiltrate without malware; email is the channel.

## References

- <https://writeups.chicken0248.fyi/HackTheBox/HTB%20Labs/HTB%20Sherlocks/%5BHTB%20Sherlocks%20Write-up%5D%20OpTinselTrace-1>
- <https://www.emclient.com/>
- <https://attack.mitre.org/techniques/T1567/002/>
