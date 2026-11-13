---
topic: Android backup forensics
tags: [mobile, android, adb, backup, sqlite, data-extraction]
---

# Android backup forensics

**English** | [🇪🇸 Español](android-backup-forensics.md)

## Concept

Android can export application data with `adb backup` when the manifest declares `android:allowBackup="true"`. The result is an `.ab` file with its own header and a compressed payload containing the app's private directory. It is a common source in forensic analysis and Mobile challenges.

## When it applies

- Extracting app data without root.
- Analysing an `.ab` backup.
- Reviewing `allowBackup` and sensitive data.
- Challenges involving SQLite, preferences or local databases.

## Requirements and conditions

- ADB and a device or emulator with the app installed.
- The APK or original `.ab` backup.
- `abe` or an equivalent unpacking tool.
- Space to extract and analyse the TAR.

## Procedure

1. Check `allowBackup` in `AndroidManifest.xml`.
2. Create the backup with `adb backup`, or receive the `.ab`.
3. Convert the `.ab` to TAR.
4. Extract and locate SQLite databases, preferences and caches.
5. Query tables and search for relevant strings.

```bash
adb backup -apk -shared -all -f backup.ab
java -jar abe.jar unpack backup.ab backup.tar
tar xf backup.tar
find . -iname '*.db' -o -iname '*.sqlite' -o -iname '*.xml'
```

## Variants

- Full device backup.
- Single-app backup.
- Logical copy through `run-as` on debug builds.
- Physical extraction with root or a user image.

## Limitations

- `allowBackup=false` blocks the logical copy.
- Some apps encrypt the database or use a keystore.
- The backup may exclude external cache files.
- Android version and vendor change the format.

## Mitigation

- Disable `allowBackup` or exclude sensitive data.
- Encrypt databases and secrets with Android Keystore.
- Do not store credentials in plaintext.
- Audit backups on corporate devices.

## Detection

- Alert on `adb backup` executions in managed fleets.
- Review `allowBackup` changes during builds.
- Monitor physical access and USB debugging.
- Compare the data inventory with the retention policy.

## References

- <https://developer.android.com/guide/topics/data/autobackup>
- <https://developer.android.com/tools/adb#backup>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1409/>
