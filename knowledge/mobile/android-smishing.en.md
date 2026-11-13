---
topic: Android smishing
tags: [mobile, android, smishing, sms, accessibility, overlay, otp]
---

# Android smishing

**English** | [🇪🇸 Español](android-smishing.md)

## Concept

Smishing combines a text message with a link or malicious APK. The resulting Trojan requests SMS and accessibility permissions to intercept OTPs, show overlays and exfiltrate data. Analysis links the message, the APK and the C2 infrastructure.

## When it applies

- A message campaign linking to an APK.
- Theft of 2FA codes.
- Accessibility or `SYSTEM_ALERT_WINDOW` permissions.
- Exfiltration to a webhook or remote server.

## Procedure

1. Preserve the SMS, sender and link.
2. Analyse the APK and its manifest.
3. Review SMS receivers and accessibility services.
4. Search for URLs, webhooks and embedded keys.
5. Correlate with network traffic and affected accounts.

```bash
apktool d sample.apk -o apk
grep -RInE 'RECEIVE_SMS|READ_SMS|BIND_ACCESSIBILITY|SYSTEM_ALERT_WINDOW' apk/AndroidManifest.xml
jadx -d jadx sample.apk
grep -RInE 'Discord|webhook|otp|AES|ECB' jadx/sources | head
```

## Variants

- A link to an APK outside the official store.
- An overlay over the banking app.
- SMS interception and forwarding.
- Encrypted exfiltration with AES-ECB.

## Limitations

- Messages may be deleted.
- The APK may be downloaded after installation.
- Permissions may be granted manually.
- The C2 may be inactive during analysis.

## Mitigation and detection

- Block APKs from unknown sources.
- Restrict accessibility and SMS permissions.
- Monitor webhooks and newly registered domains.
- Alert on sideloaded apps and read OTPs.

## References

- <https://attack.mitre.org/techniques/T1660/>
- <https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/>
- <https://www.ncsc.gov.uk/collection/mobile-device-guidance>
