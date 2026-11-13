---
sherlock: HookFlare
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, android, smishing, banking-trojan, aes-ecb, discord-webhook]
---

# HookFlare — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A smishing campaign distributes an Android banking trojan. The analyst examines the APK, SMS interception and encrypted exfiltration to a Discord webhook.

## Evidence

- Suspicious APK and declared permissions.
- SMS and call-log export.
- Network capture or C2 logs.
- Strings and embedded configuration in the APK.

```bash
sha256sum sample.apk
apktool d sample.apk -o apk
```

## Investigation

### 1. Static analysis

`AndroidManifest.xml`, SMS receivers, background services and permissions are reviewed. A receiver with `RECEIVE_SMS` plus an accessibility service suggests interception and UI control.

```bash
jadx -d jadx sample.apk
grep -RInE 'Discord|webhook|AES|ECB|sms|otp' jadx/sources | head
```

### 2. Phishing flow and 2FA

The SMS contains a link that downloads the APK. The app requests SMS and accessibility permissions, intercepts the one-time code and forwards it. The sequence is reconstructed: receipt, install, permission grant and first C2.

### 3. Encryption and exfiltration

Strings reveal an AES key and ECB mode. ECB encrypts equal blocks identically, so structured data leaks patterns. The destination is a Discord webhook acting as an exfiltration channel.

```bash
strings -a sample.apk | grep -Ei 'https://discord|webhook|key'
```

## Conclusions

- Campaign number and domain.
- Abused Android permissions and components.
- Encryption format and output channel.
- IOCs: hashes, domains and webhooks, redacted.

## Lessons

- Accessibility and SMS permissions are a high-risk combination.
- ECB does not hide data structure.
- A legitimate webhook can serve as C2 and exfiltration.

## References

- <https://www.hackthebox.com/sherlocks/HookFlare>
- <https://attack.mitre.org/techniques/T1417/>
- <https://attack.mitre.org/techniques/T1636/>
- <https://developer.android.com/guide/topics/manifest/uses-permission-element>
