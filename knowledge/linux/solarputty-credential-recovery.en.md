---
topic: SolarPuTTY — session credential recovery
tags: [linux, solarputty, credentials, encryption, instant, forensics]
---

# SolarPuTTY — session credential recovery

**English** | [🌐 Español](solarputty-credential-recovery.md)

## Idea

SolarPuTTY stores sessions and their credentials in an encrypted file (`sessions-backup.dat`). The encryption derives from a master password; if it is weak or known, credentials are recovered with tools such as `SolarPuttyDecrypt` or `SolarPuttyCracker`. On Instant, the file was in `shirohige`'s home and the decrypted password belonged to root.

## When it applies

- A `sessions-backup.dat` exists in a home, share or backup.
- The master password is weak or reused.
- A decryption tool can run on the host or the analysis machine.
- The file is not protected by a second factor.

## Procedure

1. Locate the file and confirm it belongs to SolarPuTTY.
2. Copy it to the analysis machine.
3. Try `SolarPuttyCracker` with a wordlist.
4. Alternatively, use `SolarPuttyDecrypt` when the master password is known.
5. Reuse the recovered credentials over SSH, RDP or other services.

## Commands

```bash
file sessions-backup.dat
strings sessions-backup.dat | head
python3 SolarPuttyCracker.py sessions-backup.dat -w /usr/share/wordlists/rockyou.txt
```

```powershell
SolarPuttyDecrypt.exe sessions-backup.dat <MASTER_PASSWORD>
```

## Variants

- Crack with `hashcat` if the tool extracts a hash.
- Search for the master password in configuration files or notes.
- Use a copy of the SolarPuTTY profile in `%APPDATA%`.
- Decrypt on a Windows host with the same version.
- Reuse the master password for other files.

## Limitations

- A strong master password makes cracking infeasible.
- The tool must match the file format.
- The file may be corrupt or incomplete.
- Decryption requires running third-party code in a controlled environment.
- Recovered credentials may have expired.

## Mitigation

- Use long, unique master passwords.
- Protect session files with restrictive permissions.
- Do not store root credentials in desktop tools.
- Rotate credentials and enforce MFA on SSH/RDP.
- Encrypt backups and limit access.

## Detection

- Access to `sessions-backup.dat` from unusual processes.
- Copies of the file leaving the host.
- `su` or SSH attempts with recovered credentials.
- Execution of `SolarPuttyCracker` or `SolarPuttyDecrypt`.
- Desktop passwords used on privileged accounts.

## References

- [0xdf — Instant](https://0xdf.gitlab.io/2025/03/01/htb-instant.html)
- [GitHub — SolarPuttyDecrypt](https://github.com/VoidSec/SolarPuttyDecrypt)
- [GitHub — SolarPuttyCracker](https://github.com/ItsWatchMakerr/SolarPuttyCracker)
- [Instant writeup](../../machines/linux/instant/README.en.md)
