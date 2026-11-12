---
sherlock: APTNightmare
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, memory, cobalt-strike, linux, windows]
---

# APTNightmare — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

An APT campaign compromises a Linux web server and uses the CEO as the next target. A network capture, server memory dump, Ubuntu profile and partial copy of the CEO's disk are provided. Reconstruct access, the reverse shell, persistence and second-stage delivery.

## Evidence

- `traffic.pcapng`: ~52-minute capture.
- `Memory_WebServer.mem`: web server memory.
- `Ubuntu_5.3.0-70-generic_profile.zip`: `/boot` and `/tools`.
- `DiskImage_CEO-US.zip`: partial `C:` copy from the CEO.

```bash
sha256sum traffic.pcapng Memory_WebServer.mem DiskImage_CEO-US.zip
capinfos traffic.pcapng
```

## Investigation

### 1. Inventory and triage

Start with the capture; it provides the timeline and flows:

```bash
tshark -r traffic.pcapng -q -z conv,tcp
tshark -r traffic.pcapng -Y 'http.request' -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
```

Identify the compromised host, the attacker and the reverse-shell ports.

### 2. Timeline

- First HTTP contact and web server exploitation.
- Reverse connection and interactive commands.
- `crontab` modification for persistence.
- Download of a binary from the compromised server.
- Attachment delivery to the CEO and Windows execution.

The capture spans 2024-02-05 02:30:40–03:23:02; normalise to UTC.

### 3. Key artefact

The PCAP holds the reverse-shell channel. Following it reveals persistence commands and the second-stage download. In memory, `strings` and `grep` locate the binary and C2 configuration when Volatility does not recognise the profile.

```bash
strings Memory_WebServer.mem > mem.strings
grep -iE 'cron|wget|curl|powershell|\.exe' mem.strings | head
python3 1768.py -r download.exe
```

`1768.py` identifies the Cobalt Strike beacon. On the CEO disk, LNK files and `$MFT` reveal the attachment path and scheduled task.

## Findings

- The Linux server was the entry point and initial C2.
- The attacker used cron for persistence and distributed a binary through the compromised server.
- The CEO executed an attachment that installed a beacon and a scheduled task.
- IOCs are the C2 IP/port, binary hash and attachment name.

## Lessons

- PCAP can reconstruct a full reverse shell without logs.
- `strings` remains useful when the memory profile fails.
- A compromised web server can serve the second stage.
- The chain crosses Linux and Windows; keep both timelines.

## References

- <https://mwalkowski.com/post/sherlock-aptnightmare>
- <https://github.com/DidierStevens/DidierStevensSuite/blob/master/1768.py>
- <https://attack.mitre.org/techniques/T1059/004/>
