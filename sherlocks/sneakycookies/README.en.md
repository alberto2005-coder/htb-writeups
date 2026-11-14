---
sherlock: SneakyCookies
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, lnk, phishing, srum, evtx]
---

# SneakyCookies — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A company user receives an email with an alleged PDF. The mail filter was under maintenance and the file was opened. A user-profile triage and system logs are provided to reconstruct the compromise.

## Evidence

- `TRIAGE-L3-BELLS` with `Bingle Jollybeard`'s profile.
- `christmas_slab.pdf.lnk`.
- EVTX, SRUM and files under `%TEMP%`.

```bash
sha256sum christmas_slab.pdf.lnk
LECmd.exe -f christmas_slab.pdf.lnk
```

## Investigation

### 1. Inventory and triage

`LECmd` shows the LNK points to `ssh.exe` with arguments that download an executable from an external host. The filename imitates a PDF. Review downloads, prefetch and child processes.

```bash
LECmd.exe -f christmas_slab.pdf.lnk --csv out
```

### 2. Timeline

The LNK runs from `Downloads`; `ssh.exe` uses `-o PermitLocalCommand=yes` and `LocalCommand` to copy and launch a binary. C2 connections and a local account creation follow. EVTX and SRUM confirm the times.

```bash
EvtxECmd.exe -d C/Windows/System32/winevt/Logs --csv evtx
SrumECmd.exe -d C/Windows/System32/SRU --csv srum
```

### 3. Key artifact

The SRUM stream shows the executable's traffic and sent volume. The created account is added to local administrators. The binary name and C2 host are the main IOCs.

## Conclusions

- Initial access was an LNK disguised as a PDF.
- `ssh.exe` was used as a LOLBin to download and execute.
- The attacker established persistence with a local account.
- Rotate credentials and review other profiles.

## Lessons

- Analyze LNKs with `LECmd`, not just `strings`.
- `ssh.exe` can run local commands.
- SRUM provides network and resource-usage evidence.
- A failed mail filter must not stop monitoring.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/SneakyCookies>
- <https://attack.mitre.org/techniques/T1204/002/>
