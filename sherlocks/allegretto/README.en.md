---
sherlock: Allegretto
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, bitlocker, ewf, registry, thunderbird, usb]
---

# Allegretto — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original evidence or literal answers.

## TL;DR

Investigation of a computer seized from a suspect. The EWF image is BitLocker-protected; the recovery key appears in the user's documents. Inside, NTUSER.DAT/SOFTWARE are analysed with RECmd, the Thunderbird profile is parsed, and a deleted KML in the Recycle Bin reveals coordinates.

## Scenario

Police seize a suspected drug dealer's computer; the suspect uses the dark web and encrypted storage. Reconstruct identities, email, locations and criminal activity from the artifacts.

## Artifacts

- EWF forensic image.
- BitLocker volume and recovery key in documents.
- `NTUSER.DAT` and `SOFTWARE` hives.
- Thunderbird profile (`prefs.js`, `ImapMail`, `Local Folders`).
- USB image and Recycle Bin.

## Methodology

1. Mount the EWF image with `ewfmount` and identify the BitLocker volume.
2. Use `dissect.fve` or equivalent to decrypt with the recovery key.
3. Mount NTFS with `dissect.ntfs` or `ntfs-3g`.
4. Process hives with `RECmd` and a batch file; review execution, USB and applications.
5. Parse Thunderbird: accounts in `prefs.js`, mail in `ImapMail`, contacts.
6. Review the Recycle Bin (`$R`/`$I`) and recover the deleted KML with coordinates.

```bash
ewfmount evidence.E01 /mnt/ewf
dissect.fve /mnt/ewf/ewf1 /mnt/bitlocker --recovery-key <KEY>
```

## Sample questions

- Which dark web identity does the suspect use?
- What is their contact email?
- Which mail client and accounts are configured?
- Which deleted file contained the location?
- What coordinates does the KML reveal?

## Tools

`ewfmount`, `dissect.fve`, `dissect.ntfs`, `RECmd`, `DB Browser for SQLite`, `unzip`.

## Evidence and redaction

Screenshots of hives, Thunderbird and the Recycle Bin are kept with addresses, emails and coordinates redacted. No literal answers are published.

## Lessons learned

- The recovery key may live on the same machine.
- BitLocker does not prevent analysis if the key is found.
- Thunderbird stores accounts and mail in cleartext.
- The Recycle Bin and USB metadata are key sources.

## Detection

- Monitor forensic imaging and mounting on corporate hosts.
- Audit access to BitLocker recovery keys.
- Watch for bulk mail-profile exports.
- Restrict unencrypted USB use.

## References

- <https://app.hackthebox.com/sherlocks/Allegretto>
- <https://learn.microsoft.com/en-us/windows/security/information-protection/bitlocker/>
- <https://github.com/fox-it/dissect>
