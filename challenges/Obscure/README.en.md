---
challenge: Obscure
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, webshell, keepass, john, obfuscation]
type: Forensics
---

# Obscure — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; the flag is not published.

## Brief

You get the traffic capture of a compromised web server and must reconstruct what the attacker did and what was taken.

## Evidence

```text
19-05-21_22532255.pcap    capture of the incident
```

## Method

### 1. See what was said

```bash
tshark -r 19-05-21_22532255.pcap -q -z conv,tcp
tshark -r 19-05-21_22532255.pcap -Y "http.request" -T fields -e http.request.method -e http.request.uri | sort | uniq -c
```

The interest is in the `POST` requests to a single script, always the same name: that is where the payload travels.

### 2. Follow the whole stream

```bash
tshark -r 19-05-21_22532255.pcap -q -z follow,tcp,ascii,0
```

The `POST` body carries a parameter with a **base64** blob; decoded, it is not readable PHP but binary data: there is another layer.

### 3. Undo the obfuscation

The usual pattern is base64 → **zlib** → **XOR** with a single-byte key or one derived from a string inside the blob:

```python
import base64, zlib
raw = base64.b64decode(blob)
data = zlib.decompress(raw)
print(bytes(b ^ 0x5a for b in data).decode("latin-1"))
```

The result is the **webshell** the attacker uploaded: a PHP script with the command runner (`support.php` in the site root). That is the proof of initial access and the answer to "what did they leave behind?".

### 4. What else was pulled

Repeating the stream follow exposes two more files: a victim `to-do.txt` and a **KeePass** database (`pwdb.kdbx`). Extract them straight from `tshark`:

```bash
tshark -r 19-05-21_22532255.pcap --export-objects http,exported/
ls -l exported/
```

### 5. Open the manager

```bash
keepass2john pwdb.kdbx > kdbx.hash
john --wordlist=/usr/share/wordlists/rockyou.txt kdbx.hash
keepassxc-cli show -s pwdb.kdbx <entry>
```

With the cracked password the database opens and the flag sits in one of its entries.

## Findings

- The compromise was a **webshell upload** over HTTP `POST`, not a service exploit.
- Payload obfuscation is base64 + compression + XOR: three layers, all reversible without the attacker's key.
- The real theft is the password manager: the capture holds the database and its password falls to a dictionary.

## Lessons

- On a PCAP, `follow,tcp` plus `--export-objects` settles most of the work before opening Wireshark.
- A base64 blob that does not decode to text signals compression, not encryption.
- A `.kdbx` in the traffic compromises every credential inside it.
- Mitigation: upload validation, write permissions outside the docroot, and a strong master password on the manager.
