---
sherlock: CrewCrow
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, zoom, dpapi, ntlm, credential-access]
---

# CrewCrow — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Zoom meeting is used as a pretext for an intrusion. The analyst examines application artefacts, DPAPI-protected credentials and an encrypted meeting database.

## Evidence

- Windows user profile.
- Zoom directories under `AppData`.
- DPAPI blobs and user hives.
- Zoom database and meeting logs.
- Event and authentication log export.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Zoom artefacts

Configuration, caches, meeting history and log files are located. Paths and versions identify the account and host.

```powershell
Get-ChildItem "$env:APPDATA\Zoom" -Recurse -Force
```

### 2. DPAPI

User secrets are protected by the DPAPI master key. With the profile and the user's password or hash, blobs are decrypted; without them, the analyst documents which secret is out of reach.

```powershell
dpapi::masterkey /in:<MASTERKEY> /sid:<SID> /password:<PASSWORD>
```

### 3. Database and credentials

The Zoom database may be encrypted and contain meeting IDs and passwords. NTLM hashes and offline cracking are also reviewed. The timeline correlates profile access, decryption and meeting connection.

## Conclusions

- Account and host involved.
- Recovered secrets and method.
- Meeting, identifier and participants.
- IOCs: paths, accounts and hashes, redacted.

## Lessons

- Videoconferencing apps store more metadata than users see.
- DPAPI depends on user context; without the profile it cannot be decrypted.
- An encrypted database may be useless without the key, but its metadata is still evidence.

## References

- <https://www.hackthebox.com/sherlocks/CrewCrow>
- <https://attack.mitre.org/techniques/T1555/003/>
- <https://learn.microsoft.com/en-us/windows/win32/seccng/cng-dpapi>
- <https://www.zoom.com/en/trust/security/>
