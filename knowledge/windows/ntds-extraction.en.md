---
topic: NTDS extraction
tags: [windows, active-directory, ntds, secretsdump, dcsync, credentials]
---

# NTDS extraction

**English** | [🇪🇸 Español](ntds-extraction.md)

## Concept

`NTDS.dit` is the Active Directory database and contains domain account hashes. It can be extracted from a domain controller with a volume copy, administrative access or DCSync, and combined with the `SYSTEM` hive to decrypt the hashes.

## When it applies

- A compromised domain controller.
- Replication rights or DCSync.
- A domain controller backup.
- Administrative access to the disk.

## Procedure

1. Confirm privileges on the DC.
2. Copy `NTDS.dit` or use DCSync.
3. Obtain the `SYSTEM` hive.
4. Extract hashes with `secretsdump`.
5. Reuse or crack the hashes.

```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
impacket-secretsdump <DOMAIN>/<USER>:'<PASSWORD>'@<DC> -just-dc
vssadmin create shadow /for=C:
```

## Variants

- DCSync with replication rights.
- Copy with `ntdsutil` or VSS.
- Extraction from a backup.
- Dumping service-account hashes.

## Limitations

- Elevated privileges are required.
- Antivirus may detect `secretsdump`.
- The DC may block the copy.
- Hashes may require cracking.

## Mitigation and detection

- Restrict replication rights.
- Protect backups and physical access.
- Monitor DCSync (4662) and VSS copies.
- Rotate credentials after exposure.

## References

- <https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj574173(v=ws.11)>
- <https://attack.mitre.org/techniques/T1003/003/>
- <https://github.com/fortra/impacket>
