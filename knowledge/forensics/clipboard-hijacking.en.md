---
topic: Clipboard hijacking
tags: [forensics, malware, clipboard, cryptocurrency, windows, phorpiex]
---

# Clipboard hijacking

**English** | [🇪🇸 Español](clipboard-hijacking.md)

## Concept

A clipper registers as a Windows clipboard viewer and reacts to `WM_DRAWCLIPBOARD`. When it detects a wallet address, it replaces it with the attacker's. The victim pastes a different address than the one copied and the transaction is lost.

## When it applies

- Binaries importing `SetClipboardViewer`, `OpenClipboard` or `SetClipboardData`.
- Users reporting altered cryptocurrency addresses.
- Malware with persistence and locale checks.
- Samples querying C2 before acting.

## Procedure

1. Review the binary's imports and strings.
2. Confirm registration in the viewer chain.
3. Locate the wallet pattern and replacement address.
4. Review persistence and C2.
5. Correlate with the on-chain transaction.

```text
SetClipboardViewer → WM_DRAWCLIPBOARD → OpenClipboard
→ GetClipboardData → EmptyClipboard → SetClipboardData
```

## Variants

- Replacing BTC, ETH or USDT addresses.
- Copying the binary under a service name.
- Locale checks to avoid specific countries.
- USB spreading.
- Using ENS or lookalike domains.

## Limitations

- The user must copy a valid address.
- The format must match the searched pattern.
- Some EDR blocks clipboard manipulation.
- The replacement address may be inactive.

## Mitigation and detection

- Verify the address after pasting and before signing.
- Use a hardware wallet with an on-screen confirmation.
- Block unsigned binaries and monitor clipboard viewers.
- Alert on processes calling `SetClipboardData` and wallet changes.

## References

- <https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard>
- <https://attack.mitre.org/techniques/T1115/>
- <https://attack.mitre.org/techniques/T1091/>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
