---
sherlock: Detroit becomes Human
domain: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, msi, browser-extension, mft, prefetch]
---

# Detroit becomes Human — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

A Forela sysadmin downloads an alleged AI tool from a social-media ad. After installing it, the application is nowhere to be found and he becomes suspicious. A partial disk copy with Prefetch, EVTX, user profiles and `$MFT` is provided; reconstruct the installation, the script it runs and the browser extension used for persistence.

## Evidence

- `C:` copy with ~492 artefacts of interest.
- `Prefetch`, `Amcache`, EVTX and `$MFT`.
- User profile with `Downloads`, `AppData` and browsers.
- Edge/Chrome history and extension database.

```bash
sha256sum detroit.zip
unzip -l detroit.zip | head -40
```

## Investigation

### 1. Inventory and triage

Start with the browser, since the ad and download are the origin:

```text
C/Users/<USER>/AppData/Local/Microsoft/Edge/User Data/Default/History
C/Users/<USER>/AppData/Local/Google/Chrome/User Data/Default/History
```

```bash
sqlite3 History "select url, title, last_visit_time from urls order by last_visit_time desc limit 30;"
sqlite3 History "select tab_url, target_path, start_time from downloads;"
```

History shows the sponsored post and the MSI download.

### 2. Timeline

- Ad visit and MSI download.
- Installation: event 11707 (MSI) plus service/file creation.
- `ru.ps1` execution from a Google-like path.
- Chrome extension and `content.js` creation.
- Deletion of the installation RAR.

```bash
chainsaw search -t 'Event.System.EventID: =11707' --skip-errors C/Windows/System32
MFTECmd.exe -f '$MFT' --csv mft.csv
```

### 3. Key artefact

The MSI installs a Chrome extension in a folder impersonating Google. `content.js` checks `localStorage` and messages `background.js` to run the main function. The extension survives browser restarts and is the persistence.

```text
ad -> MSI -> ru.ps1 -> Chrome extension -> background.js/content.js
```

`$MFT` confirms creation of the script and RAR, and deletion of the installer. The Any.run report for the MSI provides the original name and behaviour.

## Findings

- The user installed a fake MSI from an ad.
- The installer deployed a PowerShell script and a Chrome extension.
- The extension is both persistence and execution channel.
- IOCs are the MSI name/hash, `ru.ps1` path, extension and RAR.

## Lessons

- Sponsored ads are a malware distribution vector.
- An MSI leaves 11707 events and `Program Files` changes.
- Chrome extensions are user-level persistence and easy to overlook.
- `$MFT` reconstructs installation even after the installer is deleted.

## References

- <https://mwalkowski.com/post/sherlock-detroit-becomes-human>
- <https://learn.microsoft.com/en-us/windows/win32/msi/event-logging>
- <https://attack.mitre.org/techniques/T1176/>
