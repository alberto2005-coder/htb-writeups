---
sherlock: ShadowBait
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Windows logs (Sysmon, PowerShell, Security) from a compromised workstation
tools: [Hayabusa, EvtxECmd, Timeline Explorer, grep]
---

# ShadowBait — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

User Steven opens an Office document that arrived by email. From there the workstation starts generating activity: PowerShell, downloads, credential access and persistence. The host logs are provided to rebuild the chain.

## Evidence

- Windows event channels: Sysmon, PowerShell (including *Script Block Logging*) and Security.

## Method

1. **Turn everything into one timeline** — with tens of thousands of events, this is what makes the analysis feasible:

```bash
hayabusa csv-timeline -d ./logs -o timeline.csv
```

2. **Malicious document**: find Office child processes that should never exist.

```text
EventID 1 (Sysmon) | ParentImage ends with WINWORD.EXE
```

3. **Staging**: the document launches PowerShell; downloads show up (`Net.WebClient`, `Invoke-WebRequest`, `certutil -urlcache`) and code runs in memory.

```text
EventID 4104 | ScriptBlockText contains DownloadString
```

4. **C2**: the dropped binary (`OpenDLL.exe`) connects to the attacker host; Sysmon EventID 3 gives IP and port (`192.168.204.152:8899`).

5. **Credential access**: DPAPI abuse against stored `PSCredential` blobs; look for `ConvertTo-SecureString`, `Export-Clixml` and `AppData\Roaming\Microsoft\Credentials`.

6. **Persistence and elevation**: scheduled tasks, new services, `EventID 7045`, and `Run`/`RunOnce` registry changes.

## What it teaches

- *Script Block Logging* (4104) is the best source for what PowerShell executed and with which arguments.
- A single timeline turns a multi-hour investigation into a sequential read.
- DPAPI protects secrets from **other users**, not from an attacker already running as that user.

## Pitfalls

- **Volume**: without a CSV first it is easy to get lost; filter by process and hour.
- **Update noise**: `svchost`, `OneDrive` and `Teams` produce legitimate downloads; the discriminator is the parent (Office).
- **Time zone**: EVTX stores UTC; note the conversion before answering.
