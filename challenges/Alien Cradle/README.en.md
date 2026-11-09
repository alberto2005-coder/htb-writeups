---
challenge: Alien Cradle
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, powershell, deobfuscation, download-cradle]
---

# Alien Cradle — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

You get `cradle.ps1`, an obfuscated **PowerShell download cradle**. It checks the identity (`secret_HQ\Arth`), downloads a second stage with `WebClient` and runs it through `IEX`: that remote payload is a decoy. The flag sits **inside the script**, assembled by concatenating strings.

## Evidence

- `cradle.ps1` (one very long line).

## Method

1. **Format** it to read: it is minified.

```bash
sed 's/;/;\n/g' cradle.ps1 | head -40
```

2. **Spot the pattern**: `New-Object Net.WebClient`, `.DownloadString(...)` and `IEX(...)` are the cradle signature; the leading `if` on `WindowsIdentity.GetCurrent().Name` is a gate to run only on the target host.

3. **Ignore the decoy**: the remote content is not needed and probably unavailable. The information is in the local code.

4. **Rebuild the string**: near the end there is something like `$f='H'+'T'+'B'+'{p0w3rs'+'h3ll'+...`. Concatenate the literals in order.

```powershell
$f = 'H'+'T'+'B'+'...'   # evaluate only this assignment
```

5. **Read** the result: that is the flag.

## Pitfalls

- **Running it**: do not. Analysing is enough; executing challenge code is unnecessary.
- **Obfuscation**: intermediate variables and `-join` may appear; follow the assignment flow.
- **Single line**: without formatting the literals get lost.

## Lessons

- A cradle is the classic staging pattern: download and execute in memory.
- Concatenation obfuscation is undone by reading, not running.
- An identity `if` is both sandbox detection and target selection.
