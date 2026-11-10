---
sherlock: Heist
domain: DFIR
difficulty: Hard
platform: Hack The Box
evidence: Email, PCAP and a partial KAPE acquisition of a Windows host
tools: [EvtxECmd, PECmd, MFTECmd, SrumECmd, Wireshark, Timeline Explorer]
state: Active
tags: [dfir, phishing, redline, pcap, srum, mft, t1566.001]
---

# Heist — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Active. Investigation notes; no platform answers.

## Scenario

An insurance company employee opens an email about an alleged partnership. Days later the Blue Team gets a tip from the mail platform: the victim's credentials are for sale. The original email, a network capture and a partial disk acquisition are provided.

## Evidence

- `Email.eml`: the message the victim received.
- `Heist.pcapng`: network capture from the employee's segment.
- `Kape_Acquisition.zip`: ~917 files, a partial copy of `C:\` (hives, `$MFT`, Prefetch, profiles, `SRUDB.dat`).

```bash
sha256sum Email.eml Heist.pcapng Kape_Acquisition.zip
```

## Investigation

### 1. Inventory and triage

Three guiding questions: when did the email arrive, what did the user download, and what left the network. The `.eml` pins the time through the `Received` header (UTC) and the download domain; the PCAP says whether there was C2; the acquisition fills in the rest.

```bash
grep -iE '^(Received|From|Return-Path|Message-ID):' Email.eml
```

The message arrives at **2023-04-11 08:55:22 UTC** and the download link points to `doc-0s-5g-docs.googleusercontent.com` (Google Docs), a hop that bypasses the corporate URL filter. The downloaded ZIP is `Forela-Partnership.zip`.

### 2. Timeline

Chrome's history is a SQLite database with two useful tables, `downloads` and `download_url_chains`; `last_visit_time` is WebKit time (microseconds since 1601-01-01):

```bash
sqlite3 "C/Users/<user>/AppData/Local/Google/Chrome/User Data/Default/History" \
  "select target_path, tab_url, datetime(last_visit_time/1000000-11644473600,'unixepoch') from downloads;"
```

The ZIP download lands at **10:19:24**. Prefetch confirms the lure executed:

```bash
PECmd.exe -f "C/Windows/Prefetch/PARTNERSHIP.PDF.EXE-CCA24020.pf" --csv out --csvf pecmd.csv
MFTECmd.exe -f '$MFT' --csv out --csvf mft.csv
```

`Partnership.pdf.exe` runs at **10:20:06** and drops `SI168290.EXE`, `UN598654.EXE`, then `PRO5093.EXE`, `QU2705.EXE`: random six-character names, typical of a dropper.

### 3. Key artifact

In the PCAP, the HTTP stream to `176.113.115.145:4125` carries `http://tempuri.org/Entity/Id1`, the serialization signature of **RedLine Stealer**. The process doing the exfiltration is:

```text
C:\Users\<user>\AppData\Local\Temp\IXP001.TMP\qu2705.exe   (PID 3924)
```

The detail that closes the case is not in the PCAP but in **SRUM**: how much that PID sent.

```bash
SrumECmd.exe -f "C/Windows/System32/SRU/SRUDB.dat" -r "C/Windows/System32/config/SOFTWARE" --csv out
```

`BytesSent` = **107059** for that process, consistent with the capture and with credential exfiltration.

## Findings

- Entry via phishing with a Google Docs link and a ZIP holding a double-extension executable.
- RedLine stole browser credentials (including a Discord token) and sent them over HTTP to `176.113.115.145:4125`.
- The PCAP gives the destination; SRUM gives the actual volume, which the capture alone cannot prove.

## Lessons

- A `googleusercontent.com` link is not "Google traffic": look at the path and the downloaded file.
- Chrome history in WebKit time needs `last_visit_time/1000000-11644473600`; without it the timeline does not line up.
- Prefetch + MFT give execution and file creation; SRUM adds bytes sent per process, which is the exfiltration evidence.
- `tempuri.org/Entity/Id1` is a family signature, not a legitimate service's noise.

## Mitigations and detection

- Block executables from user paths (`AppData\Local\Temp`) and double-extension attachments.
- Proxy with full-URL inspection and block downloads from unapproved storage domains.
- Detection: Sysmon 1 with `*.pdf.exe`, creation of six-character files in `Temp`, connections to IP-only hosts with `POST` to `/rj...`, and `BytesSent` spikes in SRUM for user processes.
- Force rotation of browser-saved credentials after this kind of incident.

MITRE: T1566.001 (spearphishing attachment), T1204.002 (malicious file), T1555.003 (credentials from web browsers), T1041 (exfiltration over C2), T1071.001 (web protocols).

## References

- <https://mwalkowski.com/post/sherlock-heist>
- <https://github.com/EricZimmerman/Srum>
- <https://learn.microsoft.com/en-us/windows/win32/sysinfo/srum>
- <https://www.ired.team/offensive-security/credential-access-and-credential-dumping>
