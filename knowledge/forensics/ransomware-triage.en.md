---
topic: Ransomware triage
tags: [forensics, ransomware, encryption, shadow-copies, timeline, recovery]
---

# Ransomware triage

**English** | [🇪🇸 Español](ransomware-triage.md)

## Concept

Ransomware triage reconstructs initial access, propagation, encryption and the ransom note. The immediate goal is containment, evidence preservation and locating clean copies; later analysis identifies the family and scope.

## When it applies

- Encrypted files or a new extension.
- A ransom note in directories.
- Deleted shadow copies.
- Accounts or services used to spread.

## Procedure

1. Isolate hosts without powering off memory.
2. Preserve the note, binaries and logs.
3. Review shadow copies, backups and volumes.
4. Build a timeline of encryption and access.
5. Identify the family and scope.

```powershell
vssadmin list shadows
Get-ChildItem C:\ -Recurse -Filter *.txt -ErrorAction SilentlyContinue | Select-String -Pattern 'ransom|decrypt'
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625} -MaxEvents 100
```

## Variants

- Fast-encrypting ransomware with a note.
- Shadow copy deletion.
- Propagation over SMB or GPO.
- Double extortion with prior exfiltration.

## Limitations

- Encryption may be irreversible without the key.
- Logs may have been deleted.
- The note may be generic or fake.
- Recovery depends on intact backups.

## Mitigation and detection

- Immutable, tested backups.
- Segmentation and least privilege.
- Monitor shadow copy deletion and bulk encryption.
- Rehearse response and evidence preservation.

## References

- <https://www.cisa.gov/stopransomware>
- <https://attack.mitre.org/techniques/T1486/>
- <https://www.sans.org/white-papers/ransomware-response/>
