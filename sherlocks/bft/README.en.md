---
sherlock: BFT
domain: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, mft, ntfs, timestomp, zone-identifier, resident-data, mftecmd]
---

# BFT — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

Only one file: the raw **$MFT** (Master File Table) of a compromised machine. From it, reconstruct the intrusion: what was downloaded, where it was extracted, which script ran, and which C2 it calls.

## Evidence

```text
mft.raw
```

## Investigation

### 1. Parse the MFT

```bash
MFTECmd.exe -f mft.raw --csv out/
```

Open the CSV in Timeline Explorer. Each record is 1024 bytes, so a record's position is `entry × 1024`.

### 2. Delivery

Filter on the user's Downloads `ParentPath` and sort by time: a **ZIP** was downloaded, and minutes later a folder with the same base name appears. The ZIP name is the first delivery artefact.

The zone flow (`Zone.Identifier`) marks the file as internet-downloaded: `Mark-of-the-Web`, which survives extraction only if the container propagates it.

### 3. The script and timestomping

Inside the extracted folder sits a `.bat` named like an invoice, in a suspiciously nested path (`invoice/invoices/`). Compare the record's two timestamp sets:

- `$STANDARD_INFORMATION` (what the user sees)
- `$FILE_NAME` (what NTFS keeps at creation)

If `$SI` is far older than `$FN`, someone edited it: **timestomping** (T1070.006).

### 4. Resident content in the MFT

Small files live **inside** the record, in the resident `$DATA` attribute. No need to recover the file from disk: jump to `entry × 1024` in a hex editor and read it.

```text
offset = 23436 * 1024 = 0x16E3000
```

The full `.bat` is there, with the C2 IP and port in cleartext.

## Findings

- Delivery: ZIP downloaded from the internet into the user's folder.
- Execution: `.bat` script disguised as an invoice.
- Evasion: timestomping to make the script look old.
- C2: IP and port readable from the record's resident `$DATA`.

## Lessons

- The MFT gives name, parent path, size and **several** timestamp pairs: a complete timeline without opening the disk.
- Small files are read straight from the MFT; a hex editor replaces carving.
- Comparing `$SI` against `$FN` is the standard way to spot timestomping.
