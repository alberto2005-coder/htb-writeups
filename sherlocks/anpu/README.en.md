---
sherlock: Anpu
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, android, apk, trojan, overlay, ransomware]
---

# Anpu — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

An Android user installs an app outside the official store. Days later a ransom screen appears and contacts receive messages. The APK, a screenshot and device logs are provided.

## Evidence

- `sample.apk` and its manifest.
- Ransom-screen screenshot.
- Logcat and network traffic.

```bash
sha256sum sample.apk
apktool d sample.apk -o apk
```

## Investigation

### 1. Static analysis

Review permissions, receivers and services. Accessibility, overlay and SMS permissions signal a banking trojan or ransomware.

```bash
jadx -d jadx sample.apk
grep -R "AccessibilityService\|SYSTEM_ALERT_WINDOW" apk/AndroidManifest.xml
```

### 2. Strings and configuration

Look for URLs, keys and package names. The APK may download a second stage; identify domains and the configuration format.

```bash
strings sample.apk | grep -E 'https?://'
```

### 3. Behaviour

Logcat and PCAP show persistence, file encryption and exfiltration. The ransom screen overlays the legitimate app to capture credentials.

## Conclusions

- The APK abuses accessibility and overlays.
- The second stage downloads from an identifiable domain.
- Ransomware encrypts files and shows a ransom screen.
- Excessive permissions are the first warning.

## Lessons

- An APK can be analysed without running it.
- Permissions reveal capabilities before code.
- The second stage may be on the same server.
- Mobile analysis combines static and dynamic work.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://owasp.org/www-project-mobile-app-security/>
- <https://attack.mitre.org/techniques/T1417/>
