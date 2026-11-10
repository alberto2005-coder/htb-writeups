---
sherlock: i-like-to
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, moveit, cve-2023-34362, iis, mft, evtx, memory, webshell]
---

# i-like-to — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no platform answers published verbatim.

## Scenario

An internet-facing **MOVEit Transfer** server has been compromised. The organisation hands over a KAPE triage of the file system, the IIS logs for the day of the incident, the application database dump and a 4 GB memory image. The job is to reconstruct how the attacker got in, what they left behind and what they took.

## Evidence

```text
I-like-to-27a787c5.vmem                       memory image (no .vmss)
Triage/uploads/auto/C%3A/inetpub/logs/LogFiles/W3SVC2/u_ex230712.log
Triage/uploads/auto/C%3A/Windows/System32/winevt/Logs/   system EVTX
Triage/uploads/auto/C%3A/users/                          PSReadLine history
Triage/uploads/ntfs/%5C%5C.%5CC%3A/$MFT                  raw MFT
Triage/uploads/moveit.sql                                database dump
```

```bash
sha256sum Triage.zip I-like-to-27a787c5.vmem   # record before touching anything
```

The image has no `.vmss`, so Volatility cannot rebuild the memory layers: for that piece you are limited to `strings`.

## Investigation

### 1. Inventory and triage

Start with whatever gives context fastest: the IIS logs and the `$MFT`. The IIS log reads without tooling and gives the request sequence in UTC; the MFT is converted to CSV to get creation, modification and record-change times per file:

```bash
C:/Tools/ZimmermanTools/MFTECmd.exe -f '$MFT' --csv mft_out/
C:/Tools/ZimmermanTools/EvtxECmd.exe -d Logs --json evtx_out/
strings I-like-to-27a787c5.vmem > mem.strings
strings -e l I-like-to-27a787c5.vmem >> mem.strings
```

From the triage, open `u_ex230712.log` first: it is the only place with full HTTP requests, including method, path, status, user-agent and source IP.

### 2. Timeline

IIS logs use **UTC** in the date-time field, as do EVTX and the MFT, so correlation needs no conversion: one of the reasons this case resolves quickly.

Order of events:

1. `nmap` sweep against the server (the scanner user-agent stays in the log).
2. POST requests to `machine2.aspx` with user-agent `Ruby`: the Metasploit exploit for CVE-2023-34362, which uses that component for the SQL injection and deserialisation.
3. Service account password change (`4724`), followed by a **type 10** logon (RDP) with that same account.
4. First web shell attempt: `moveit.asp` in `C:\inetpub\wwwroot`. It fails because classic ASP is not enabled, and Defender quarantines it.
5. Second attempt: `move.aspx` in `C:\MOVEitTransfer\wwwroot`, which does execute.
6. Web shell use and data extraction.

### 3. Key artifact

The **MFT record** for `move.aspx` settles it: located in `C:\MOVEitTransfer\wwwroot`, 1400 bytes, creation time matching the log request. Its .NET compiled copy also appears under `Windows\Microsoft.NET\Framework64\v4.0.30319\Temporary ASP.NET Files\root\...`, timestamped when the attacker first ran it.

```bash
grep 'move.aspx' mft_out/*.csv | cut -d, -f6-9,20-27
```

`mem.strings` holds three more pieces:

- The web shell download command: a PowerShell `wget` pointing at the attacker IP and port 9001.
- The shell title, **awen asp.net webshell**, which identifies the family.
- The `net user` command that changed the service account password.

The SQL dump provides the instance `InstID`, the identifier used to generate the web shell token; it proves the shell came from the application itself rather than another upload channel.

## Findings

- Entry: **CVE-2023-34362** exploitation (SQL injection in MOVEit Transfer) with the Metasploit module, repeated for almost an hour.
- Persistence: ASPX web shell (`move.aspx`) in the application directory, preceded by a failed ASP attempt.
- Interactive access: service account password change and RDP with it.
- Indicators: `Ruby` user-agent on POSTs to `machine2.aspx`, requests to `move.aspx`, PowerShell `wget`, the `awen asp.net webshell` title and the .NET compile path of the shell.
- Method lesson: the failed `moveit.asp` attempt and its Defender quarantine belong in the story; skipping them leaves a hole in the timeline.

## Lessons

- An EDR blocking the first attempt does not stop the second: detection must cover `.aspx` creation by the IIS worker process.
- IIS logs and the MFT complement each other: the log says "when it was requested", the MFT says "when it existed on disk".
- PSReadLine history and memory `strings` recover commands no application log stores.
- Mitigation: patch MOVEit, restrict writes to `wwwroot`, alert on `w3wp.exe` creating executables, and watch service account password changes (`4724`).
- What the organisation is missing: a complete memory capture (with `.vmss`) and IIS log retention beyond a few days.

MITRE: T1190 (exploit public-facing application), T1505.003 (web shell), T1059.001 (PowerShell), T1021.001 (RDP), T1098 (account manipulation).
