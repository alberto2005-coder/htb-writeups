---
sherlock: DroidPhish
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, android, apk, phishing, mobile]
---

# DroidPhish — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation note; no literal platform answers.

## Scenario

A disk image from a compromised Android device is provided. Several employees received a phishing email and are suspected of installing a malicious application. The task is to determine when the device booted, which mail app was used, when the message arrived, which APK was downloaded and installed, which permissions it received and which C2 it was configured with.

## Evidence

- Android ext4 image (`android-x86`), mountable or explorable with `debugfs`.
- `data/data/ch.protonmail.android/databases/db-mail`: Proton Mail database.
- `data/data/com.android.chrome/databases/History`: Chrome history and downloads.
- `data/system/packages.xml`: package manager registry.
- `data/misc/users/0/runtime-permissions.xml`: granted permissions.
- `data/misc/bootstat/last_boot_time_utc`: boot marker.

```bash
sha256sum DroidPhish.dd
file DroidPhish.dd
debugfs -R 'ls -l /data' DroidPhish.dd
```

## Investigation

### 1. Inventory and triage

Work on a copy and with `TZ=UTC`. Android stores many times as epoch milliseconds and shell mtimes depend on the time zone.

```bash
TZ=UTC debugfs -R 'stat /data/misc/bootstat/last_boot_time_utc' DroidPhish.dd
```

Extract the `data` directory so `sqlite3` and APK tooling can be used:

```bash
debugfs -R 'rdump /data ./data' DroidPhish.dd
```

### 2. Timeline

- **Mail:** `db-mail` holds the subject and headers. Proton's `Received:` line is the arrival time; the `time` column may be the sender's date.
- **Download:** Chrome's `downloads` table stores the URL and target path.
- **Install:** `packages.xml` holds `it` (first install time) in epoch milliseconds; convert it to UTC.
- **Boot:** the mtime of `last_boot_time_utc` gives the reference.

```bash
sqlite3 db-mail "select subject, datetime(time/1000,'unixepoch') from MessageEntity;"
sqlite3 History "select tab_url, target_path, datetime(start_time/1000,'unixepoch') from downloads;"
```

Order the events and check that installation happens minutes after the mail and download.

### 3. Key artifact

The APK is the link. Locate the installed `base.apk`, hash it and compare it with the downloaded file:

```bash
sha256sum Download/Booking.apk
sha256sum data/app/<package>/base.apk
```

`packages.xml` maps `codePath` to the package and its install time. `runtime-permissions.xml` lists granted permissions; a high count for an alleged booking app is a red flag. In the dex, `strings` or Androguard find base64 strings that decode to a C2 IP and port.

```bash
python3 -c "from androguard.misc import AnalyzeAPK; a,d,dx=AnalyzeAPK('base.apk'); print(dx.get_strings())"
```

## Findings

- The vector was a Proton Mail phishing email linking to an APK hosted behind a Cloudflare tunnel.
- Chrome downloaded the APK and the user installed it as a fake booking app.
- The app received excessive runtime permissions and carried a base64-obfuscated C2.
- IOCs are the download URL, APK hash, package name and C2.

## Lessons

- Block or alert on APK sideloading outside the store.
- Filter links to disposable tunnel domains at the mail gateway.
- Compare requested permissions with the app's stated function.
- Static dex analysis finds encoded C2s without running the malware.
