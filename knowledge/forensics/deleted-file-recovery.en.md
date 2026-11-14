---
topic: Deleted file recovery
tags: [forensics, deleted-files, carving, ntfs, ext4, usb, photorec]
---

# Deleted file recovery

**English** | [🇪🇸 Español](deleted-file-recovery.md)

## Concept

When a file is deleted, the system frees its blocks but does not always overwrite them. Metadata and content may be recoverable from unallocated space, the recycle bin, journals or a removable device, as long as the space has not been reused.

## When it applies

- Deleted files on NTFS, ext4, FAT or exFAT.
- USB devices or disk images.
- Recovering deleted flags or documents.
- Post-incident analysis of a machine.

## Procedure

1. Create a forensic image and work on a copy.
2. Mount read-only or use recovery tools.
3. Check the recycle bin, `$Recycle.Bin` or `.Trash`.
4. Look for metadata and unallocated entries.
5. Carve by signatures if metadata is insufficient.

```bash
dd if=/dev/sdb of=usb.img bs=4M status=progress
photorec usb.img
fls -r -p usb.img | grep -i deleted
```

## Variants

- Recovery from the NTFS MFT.
- `extundelete` or `debugfs` on ext4.
- Carving PDF, ZIP or images by header.
- Files in the recycle bin or restore points.
- Recovery from a formatted USB.

## Limitations

- Reused space destroys the content.
- Some systems encrypt the disk.
- Carving can produce false positives.
- Mounting the device read-write alters evidence.

## Mitigation and detection

- Encrypt disks and removable devices.
- Use secure erase when appropriate.
- Audit image creation and recycle-bin access.
- Preserve chain of custody and hashes.

## References

- <https://www.cgsecurity.org/wiki/PhotoRec>
- <https://forensics.wiki/deleted_file_recovery/>
- <https://attack.mitre.org/techniques/T1070/004/>
- <https://csrc.nist.gov/publications/detail/sp/800-86/final>
