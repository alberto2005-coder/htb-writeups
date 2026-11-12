---
challenge: Insider
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, firefox, credentials, sqlite, firepwd]
---

# Insider — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flags.

## TL;DR

A `Mozilla` folder with an employee's Firefox profile is provided. `logins.json` holds encrypted credentials and `key4.db` the key that protects them. With the complete profile, `firepwd` decrypts the username and password for a Tomcat Manager; that password is the flag.

## Brief and surface

- Forensics, Easy, retired.
- A folder with a Firefox profile (`Mozilla/Firefox/...`) is provided.
- The goal is to recover the stored credential.

```bash
find Mozilla -type f | head -40
```

## Recon

Relevant files:

```text
Mozilla/Firefox/Profiles/<profile>/logins.json
Mozilla/Firefox/Profiles/<profile>/key4.db
Mozilla/Firefox/Profiles/<profile>/pkcs11.txt
Mozilla/Firefox/Profiles/<profile>/cert9.db
```

`logins.json` is JSON and can be read directly:

```bash
jq '.logins[] | {hostname, encryptedUsername, encryptedPassword}' logins.json
```

`encryptedUsername` and `encryptedPassword` are encrypted; they are not base64 plaintext.

## Source analysis

Firefox derives a key from `key4.db` (NSS) and the `globalSalt`. In older profiles, `key4.db` contains a `password-check` entry; `firepwd` rebuilds the key, verifies the check and decrypts each login with 3DES/AES depending on the version.

```bash
sqlite3 key4.db '.tables'
sqlite3 key4.db 'select * from metaData;'
```

There is no need to attack Firefox: the profile is complete and the user key is not protected by a master password.

## The bug

Firefox's master password is empty. Without it, the key that encrypts the store comes from `key4.db` and the profile; encryption only protects against casual reading, not against an analyst with the files. The Tomcat credential is recoverable.

## Local reproduction

```bash
git clone https://github.com/lclevy/firepwd
python3 firepwd/firepwd.py -d Mozilla/Firefox/Profiles/<profile>
```

The tool prints the hostname, username and plaintext password. Check that the host is an admin panel and that the password matches the flag format.

## Exploitation

There is no server in this challenge: exploitation is decryption.

```bash
python3 firepwd/firepwd.py -d Mozilla/Firefox/Profiles/<profile> | tee firepwd.txt
```

The correct output includes a username/password pair; the password is the flag. Redact it in evidence.

## Evidence

- `jq` showing the hostname and encrypted fields.
- `key4.db` with the `metaData` and `nssPrivate` tables.
- `firepwd` output with the password redacted.

## Lessons learned

- A Firefox profile is a complete forensic artefact: history, sessions, addons and credentials.
- `logins.json` without `key4.db` is not enough; both form the pair.
- An empty master password leaves credentials recoverable.
- `firepwd` automates NSS, but know which files it needs.

## Mitigations and detection

- Set a strong master password and lock the profile on session end.
- Never store admin credentials in the browser.
- Encrypt the disk and restrict profile permissions.
- Detection: anomalous access to `logins.json`/`key4.db` and execution of credential-recovery tooling.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/insider/>
- <https://github.com/lclevy/firepwd>
- <https://support.mozilla.org/en-US/kb/secure-firefox-primary-password>
