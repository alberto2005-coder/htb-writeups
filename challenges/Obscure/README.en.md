---
challenge: Obscure
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, webshell, keepass, john, obfuscation]
---

# Obscure — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

An attacker uploads an **obfuscated PHP webshell** (`support.php`) using base64 + zlib + XOR and `eval`. The PCAP from the minutes before the service was shut down contains the commands executed and yields a **KeePass `.kdbx`**; `keepass2john` plus a dictionary opens the vault and reveals the flag.

## Evidence

- `support.php` (obfuscated webshell) and `capture.pcap`.

## Method

1. **Understand the webshell**: peel the layers in order — base64, zlib decompression and XOR with the key embedded in the code. A trailing `eval` means the POST parameter executes code.

```bash
grep -o "base64_decode\|gzuncompress\|gzinflate\|eval" support.php
```

2. **Read the conversation**: in Wireshark, `http.request.method == POST` and `Follow → HTTP Stream`. Requests carry the command in the body; responses carry the output.

3. **Rebuild the session**: `ls -al` reveals an interesting file, `pwdb.kdbx`. Extract it from the stream or through `Export Objects → HTTP`.

4. **Crack the vault**:

```bash
keepass2john pwdb.kdbx > kdbx.hash
john --wordlist=/usr/share/wordlists/rockyou.txt kdbx.hash
```

5. **Open it** with KeePassXC and the recovered password: the flag is inside.

## Pitfalls

- **Layer order**: XOR before base64 gives nothing; follow the order in the code.
- **Corrupt kdbx**: extract the object carefully; a truncated response breaks the file.
- **Slow john**: the KeePass format is expensive; also try `hashcat -m 13400` on a GPU.

## Lessons

- An obfuscated webshell does not hide its behaviour: the final `eval` gives execution away.
- A PCAP of cleartext HTTP holds credentials, commands and exfiltrated files.
- A password manager is only as strong as its master password: if it is in a dictionary, it falls.
