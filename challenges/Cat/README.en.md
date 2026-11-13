---
challenge: Cat
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, adb-backup, sqlite, data-extraction]
---

# Cat — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app stores data in a SQLite database and allows backups through `adb backup`. The `.ab` file is converted to TAR, extracted, and the database reveals the flag.

## Prompt and surface

- Mobile, Easy, retired.
- An APK and, per the prompt, an Android backup are provided.
- The app stores information locally.

```bash
file cat.apk backup.ab
```

## Reconnaissance

- `AndroidManifest.xml` declares `android:allowBackup="true"`.
- The app does not require root to export its data.
- The backup contains the app's private directory.

```bash
apktool d cat.apk -o apk
grep -RIn 'allowBackup\|databases\|sqlite' apk/AndroidManifest.xml apk/res 2>/dev/null | head
```

## Analysis

The `.ab` format has its own header and a compressed payload. `abe` converts it to TAR; the app directory is then extracted and the database located.

```bash
java -jar abe.jar unpack backup.ab backup.tar
tar xf backup.tar
find . -iname '*.db' -o -iname '*.sqlite'
```

## Exploitation

1. Convert the backup to TAR.
2. Extract it into a working directory.
3. Open the SQLite database and list tables.
4. Search text columns for the flag.

```bash
sqlite3 apps/<PACKAGE>/db/<DB> '.tables'
sqlite3 apps/<PACKAGE>/db/<DB> "select * from <TABLE>;"
```

If no backup is available, one can be generated from an emulator with the app installed using `adb backup -apk -shared -all`.

## Evidence

- `.ab` header and TAR conversion.
- Database path inside the backup.
- SQL query with the flag redacted.

## Lessons learned

- `allowBackup` exposes private data without root.
- A backup is a complete copy of the app directory.
- SQLite is easy to inspect once extracted.

## Mitigations and detection

- Disable `allowBackup` or exclude sensitive data.
- Encrypt the database and derive keys from a secure store.
- Do not store secrets in plaintext.
- Audit backups and ADB access on corporate devices.

## References

- <https://www.hackthebox.com/challenges/Cat>
- <https://developer.android.com/guide/topics/data/autobackup>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1409/>
