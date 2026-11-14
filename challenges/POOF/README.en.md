---
challenge: POOF
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, memory, pyinstaller, ransomware, aes-cfb]
---

# POOF — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A PCAP, a memory dump and an encrypted PDF reconstruct a ransomware incident. Traffic reveals the download of a tar.gz containing a PyInstaller `configure` binary. Extracting and decompiling it reveals the AES-CFB key and IV; they decrypt the PDF and reveal the flag.

## Statement and surface

- Forensics, Easy, retired.
- `poof_capture.pcap`, `mem.dmp`, `candy_dungeon.pdf.boo` and an Ubuntu profile are provided.
- The scenario asks for the malicious URL, the process and the encryption algorithm.

```bash
unzip -l POOF.zip
```

## Reconnaissance

- The PCAP contains HTTP traffic and a `pygaming-dev-13.37.tar.gz` download.
- The `.boo` file is the encrypted PDF.
- The memory dump and profile can validate the process, but the PCAP already provides the main lead.

```bash
tshark -r poof_capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

## Code analysis

The tar.gz contains a `configure` binary. `file` and `strings` show Python 3.6 and PyInstaller references; it is not a plain native binary.

```bash
tar -xzf pygaming-dev-13.37.tar.gz
file pygaming-dev-13.37/configure
strings -n 8 pygaming-dev-13.37/configure | grep -i pyinstaller
```

Extract it with `pyinstxtractor` and decompile `configure.pyc` with `uncompyle6`. The code contains an AES-CFB encryption function with an embedded key and IV, and a routine that renames every file to `.boo`.

## Why it works

The ransomware uses a symmetric key stored in the binary. There is no key exchange or asymmetric encryption: anyone who analyzes the executable can decrypt the files. The encryption routine and the ransom note are in the bytecode.

```python
cipher = AES.new(key, AES.MODE_CFB, iv)
open(filename, "wb").write(cipher.encrypt(data))
```

## Local reproduction

```bash
python3 -m venv venv
. venv/bin/activate
pip install pycryptodome
python3 - <<'PY'
from Crypto.Cipher import AES
key = b"<KEY>"
iv = b"<IV>"
data = open("candy_dungeon.pdf.boo", "rb").read()
open("candy_dungeon.pdf", "wb").write(AES.new(key, AES.MODE_CFB, iv).decrypt(data))
PY
```

## Exploitation

1. Extract the tar.gz from the PCAP.
2. Identify the binary and the `configure` process.
3. Extract the bytecode with `pyinstxtractor`.
4. Decompile with `uncompyle6`.
5. Read the key and IV.
6. Decrypt the PDF and compute its MD5.

```bash
md5sum candy_dungeon.pdf
```

The MD5 and flag are redacted.

## Evidence

- Download URL and process name.
- `file` and `strings` output for the binary.
- Decompiled encryption function with the key redacted.
- Decrypted PDF and redacted MD5.

## Lessons learned

- PyInstaller binaries can be extracted and decompiled.
- An embedded key does not protect ransomware.
- The PCAP reconstructs the chain even when memory is large.

## Mitigations and detection

- Block binary downloads from untrusted hosts.
- Inspect PyInstaller executables before running them.
- Monitor mass creation of files with anomalous extensions.
- Alert on processes encrypting user directories and HTTP connections to compressed files.

## References

- <https://www.hackthebox.com/challenges/POOF>
- <https://github.com/extremecoders-re/pyinstxtractor>
- <https://attack.mitre.org/techniques/T1486/>
- <https://attack.mitre.org/techniques/T1059/006/>
