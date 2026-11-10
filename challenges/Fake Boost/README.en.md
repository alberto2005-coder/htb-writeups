---
challenge: Fake Boost
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, powershell, base64, aes, c2, phishing]
---

# Fake Boost — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (Cyber Apocalypse 2024). Challenge solved; no real flags.

## TL;DR

A network capture holds a phishing campaign giving away "Discord Nitro". The lure drops an obfuscated PowerShell that **reverses and base64-decodes** a string before running it. Deobfuscated, the script collects user data (including the Discord token), encrypts it with **AES-CBC** and POSTs it to `192.168.116.135:8080/rj1893rj1joijdkajwda`. The whole case is solved by exporting HTTP objects and deobfuscating without executing anything.

## Brief and surface

- Forensics, 2/5 difficulty in the event's official index.
- `forensics_fake_boost.zip` ships a single capture: `capture.pcapng`.
- No lure binary: the artifact is the traffic.

## Recon

```bash
capinfos capture.pcapng
tshark -r capture.pcapng -q -z io,phs
tshark -r capture.pcapng -q -z conv,tcp
```

```bash
mkdir -p out
tshark -r capture.pcapng --export-objects http,out
ls -l out
```

The HTTP objects include the lure HTML, the downloaded ZIP/EXE and the exfiltration `POST`s.

## Source analysis

The PowerShell shows up in a response body. Obfuscated it looks like:

```powershell
$b64 = '...'
$rev = -join ($b64[-1..-($b64.Length)])
$dec = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($rev))
Invoke-Expression $dec
```

That is: the string is reversed **and** base64. Any other order (decode without reversing) returns garbage, which is the usual mistake when copying the block by hand.

Deobfuscated, the script:

1. Reads the Discord token from `%APPDATA%\discord\Local Storage\leveldb`.
2. Gathers system information.
3. Encrypts the bundle with **AES-CBC** (key and IV embedded in the script itself).
4. POSTs the result to the attacker's URL.

## The bug

There is no vulnerability here: it is a social-engineering chain with trivial obfuscation. The forensic value is rebuilding the transformation order and identifying the egress channel, not "breaking" anything.

AES protects nothing: the key travels in the same script the attacker left on the host, so the analyst decrypts with it.

## Local reproduction

```bash
tshark -r capture.pcapng -Y 'http.response' -T fields -e http.file_data > responses.txt
```

Deobfuscate without executing:

```python
import base64, re
s = open('responses.txt', encoding='utf-8', errors='replace').read()
b64 = re.search(r"\$b64\s*=\s*'([^']+)'", s).group(1)
print(base64.b64decode(b64[::-1]).decode('utf-8', 'replace')[:800])
```

## Exploitation

1. Export objects and locate both the script and the exfiltration `POST`:

```bash
tshark -r capture.pcapng -Y 'http.request.method == "POST"' \
  -T fields -e ip.dst -e tcp.dstport -e http.request.uri
```

```text
192.168.116.135   8080   /rj1893rj1joijdkajwda
```

2. Pull the encrypted body from the `POST` (`http.file_data` of the stream) and the key/IV pair from the deobfuscated script.

3. Decrypt with AES-CBC:

```python
from Crypto.Cipher import AES
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
print(pt.rstrip(b'\x00'))
```

4. The decrypted JSON yields user, host and token, plus the flag the challenge places in the stream.

Optional tool: **PowerDecode 2.7** automates the PowerShell unpacking, but `tshark` + CyberChef by hand gets there too.

## Evidence

- HTTP object listing, the exfiltration URL and trimmed decrypted JSON.
- No real flags: values live in `private/`.

## Lessons learned

- `--export-objects http` turns a PCAP into files: it is the first command, not the last.
- Reverse-then-decode is a one-line obfuscation; order matters and must be respected.
- Encryption does not hinder exfiltration analysis when the key sits in the script.
- The `192.168.116.135:8080` destination with a random URI is the IOC to push into proxy blocks.

## Mitigations and detection

- Block attachments and double-extension downloads; the "free Nitro" lure is the classic hook.
- Proxy inspection of `POST`s to IP-only hosts and of random URIs.
- Detection: PowerShell with `FromBase64String` + `Invoke-Expression` (4104 carrying both), processes reading Discord's `leveldb`, and outbound port 8080 connections from workstations.
- Rotate the Discord token and browser credentials after the incident.

MITRE: T1566.002 (spearphishing link), T1059.001 (PowerShell), T1027 (obfuscated files or information), T1041 (exfiltration over C2), T1555.003 (credentials from web browsers).

## References

- <https://github.com/hackthebox/cyber-apocalypse-2024>
- <https://ctftime.org/writeup/38843>
- <https://v0lk3n.github.io/writeup/HTB-CyberApocalypse2024/HTB-CyberApocalypse2024-WriteUp.html>
- <https://www.wireshark.org/docs/man-pages/tshark.html>
