---
challenge: misDIRection
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, zip, directory-structure, base64, scripting]
---

# misDIRection — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flag.

## TL;DR

A ZIP contains a `.secret/` tree with directories named after characters and files named after positions. Sorting the files numerically and concatenating their directory names yields a base64 string; decoding it reveals the flag.

## Brief and surface

- Misc, Very Easy, retired.
- `misDIRection.zip` is provided.
- The ZIP uses the challenge's usual password.

```bash
file misDIRection.zip
unzip -l misDIRection.zip | head
```

## Recon

```bash
unzip -P '<ZIP_PASSWORD>' misDIRection.zip
find .secret -type f | head
```

The tree contains directories such as `.secret/S/`, `.secret/V/`, and numerically named files (`1`, `35`, `2`...). The files are empty: the name is the data.

## Source analysis

Each file represents a position and its directory the character. Sorting by file number rebuilds the sequence:

```bash
find .secret -type f | awk -F / '{ print $3, $2 }' | sort -n | awk '{ print $2 }' | tr -d '\n'
```

The result looks like base64. Decode it:

```bash
... | base64 -d
```

## The bug

Information is encoded in names, not content. The only “protection” is the weak/known ZIP password. Anyone with the structure can rebuild the message without opening the files.

## Local reproduction

```bash
unzip -P '<ZIP_PASSWORD>' misDIRection.zip -d work
cd work
find .secret -type f | awk -F / '{ print $3, $2 }' | sort -n | awk '{ print $2 }' | tr -d '\n' > out.b64
base64 -d out.b64
```

Check that numeric order is correct and positions are unique.

## Exploitation

There is no server. Exploitation is rebuilding the string and decoding it. Verify the flag on the platform and redact it.

## Evidence

- Directory/file structure.
- Redacted base64 string.
- Redacted flag.

## Lessons learned

- File and directory names are data.
- `find` + `awk` + `sort -n` reconstructs position-based sequences.
- A weak ZIP password does not protect the structure.
- Base64 is a common hint.

## Mitigations and detection

- Never store secrets in filenames.
- Encrypt the whole archive with a strong password.
- Avoid structures that reveal the message without opening content.
- Detection: in CTFs, review metadata and names; in production, DLP on files.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/misc/misdirection/>
- <https://linux.die.net/man/1/find>
- <https://en.wikipedia.org/wiki/Base64>
