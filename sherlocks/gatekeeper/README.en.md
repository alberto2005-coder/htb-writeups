---
sherlock: GateKeeper
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, macos, unified-logs, gatekeeper, safari, cve-2022-22616]
---

# GateKeeper — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A corporate Mac shows suspicious activity after the user opened a downloaded file. A collection of macOS artefacts is provided to determine how Gatekeeper was bypassed, what executed and how privileges were escalated.

## Evidence

- Unified logs (`log show` or `logarchive`).
- Safari history and downloads.
- Quarantine database and LaunchServices metadata.
- Execution, persistence and account artefacts.

```bash
log show --archive system.logarchive --start "2026-01-01" --end "2026-01-02" --style json > unified.json
```

## Investigation

### 1. Inventory and triage

Establish the host, macOS version and user session. Review downloads, mounted volumes and applications run from user paths.

```bash
sqlite3 ~/Library/History.db "select datetime(v.visit_time + 978307200, 'unixepoch'), i.url from history_visits v join history_items i on v.history_item=i.id;"
```

### 2. Timeline

- File download and first Gatekeeper prompt.
- Opening the package or binary.
- Child-process execution and network connections.
- Persistence in LaunchAgents, LaunchDaemons or login items.
- Privilege change and access to user data.

The unified log uses the system's local time; normalise to UTC for comparison.

### 3. Key artefact

The quarantine event and LaunchServices record show the file ran without the expected validation. Combined with the vulnerable version, this attributes the bypass to CVE-2022-22616; a local escalation associated with CVE-2019-8513 follows.

```bash
xattr -l <DOWNLOAD>
sqlite3 ~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2.db \
  "select datetime(LSQuarantineTimeStamp + 978307200,'unixepoch'), LSQuarantineDataURLString from LSQuarantineEvent;"
```

## Conclusions

- Which download started the chain and which app opened it.
- How the Gatekeeper check was avoided.
- Which processes and persistence remained.
- IOCs: URL, bundle, path and hash, redacted.

## Lessons

- On macOS, quarantine and LaunchServices matter as much as logs.
- A Gatekeeper bypass does not always leave an explicit event; sources must be correlated.
- User persistence can survive app removal.

## References

- <https://www.hackthebox.com/sherlocks/GateKeeper>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-22616>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-8513>
- <https://attack.mitre.org/techniques/T1553/001/>
