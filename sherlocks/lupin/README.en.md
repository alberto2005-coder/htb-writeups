---
sherlock: Lupin
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, pe, clipboard-hijacking, cryptocurrency, ssdp, static-analysis]
---

# Lupin — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A sample `optimize.exe` is shared as an optimization tool. User Samira notices that the wallet address she copies changes before she pastes it. The task is to analyze the binary, identify persistence, C2 and the theft mechanism.

## Evidence

- `optimize.exe`, 32-bit PE, 81,920 bytes.
- The sample is not executed; analysis is static.
- Tools: `pefile`, Capstone, `strings`.

```bash
sha256sum optimize.exe
file optimize.exe
python3 -c "import pefile; pe=pefile.PE('optimize.exe'); print(hex(pe.OPTIONAL_HEADER.ImageBase))"
```

## Investigation

### 1. Inventory and triage

File entropy is medium (≈6.4), it is not packed and strings are readable. The binary imports clipboard, WinINet and network functions.

```bash
python3 - <<'PY'
import math, collections
d = open("optimize.exe", "rb").read()
c = collections.Counter(d)
print(-sum(v/len(d)*math.log2(v/len(d)) for v in c.values()))
PY
```

### 2. Persistence and evasion

The malware copies itself to system locations under a service-like name, `syscrondvr.exe`. Before acting it checks its own filename and queries the locale; if the locale does not match, it stops.

- Copies itself under a fixed name to blend with services.
- `GetLocaleInfoA` as a geographic gate.
- `DeleteUrlCacheEntry` before each request to force fresh C2 data.

### 3. Clipboard theft

The binary registers as a clipboard viewer with `SetClipboardViewer` and reacts to `WM_DRAWCLIPBOARD`. When it detects a wallet address, it opens the clipboard, empties it and writes the attacker's address with `SetClipboardData`.

```text
SetClipboardViewer → WM_DRAWCLIPBOARD → OpenClipboard → EmptyClipboard → SetClipboardData
```

It also sends SSDP `M-SEARCH` to `239.255.255.250:1900`, a network-discovery behavior.

### 4. Attribution and blockchain

The attacker address is hardcoded. Resolve the victim's ENS name and follow the transaction on a block explorer; the transfer matches the incident date. The behavior set (clipper, service-like copy, USB spreading) matches the Phorpiex family.

## Conclusions

- The malware replaces wallet addresses in the clipboard.
- Persistence uses a service-like name and a locale check.
- C2 requests invalidate the cache first.
- On-chain tracing confirms impact.

## Lessons

- A UI-less binary registering a clipboard viewer is suspicious.
- Verifying the wallet after pasting is a simple, effective defense.
- Behavior-based attribution must be confirmed with hashes and intelligence.

## References

- <https://www.hackthebox.com/sherlocks/Lupin>
- <https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard>
- <https://attack.mitre.org/techniques/T1115/>
- <https://attack.mitre.org/techniques/T1091/>
