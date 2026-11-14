---
challenge: Wrong Spooky Season
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, reverse-shell, tshark]
---

# Wrong Spooky Season — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A PCAP contains a reverse shell. Following the TCP stream reveals the connection command, the interactive shell and the flag read. Nothing is encrypted.

## Prompt and surface

- Forensics, Easy, retired.
- A `.pcap` is provided.
- The prompt describes suspicious Halloween activity.

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z conv,tcp
```

## Reconnaissance

- TCP traffic on a high port.
- An internal host connects to an external one.
- Readable ASCII payloads.

## Code analysis

There is no code to analyse. Identify streams and look for the one carrying a shell. The command usually includes `bash -i`, `nc` or `mkfifo`.

```bash
tshark -r capture.pcap -Y 'tcp contains "bash"' -T fields -e tcp.stream
```

## Why it works

The reverse shell is unencrypted. Anyone with the PCAP can rebuild the session, commands and output, including the flag.

## Local reproduction

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<STREAM>
```

- Follow the stream.
- Note the connection command and user.
- Extract the `cat`/`type` output.

## Exploitation

```bash
tshark -r capture.pcap -q -z follow,tcp,raw,<STREAM> | xxd -r -p
```

The flag appears in the output; it is redacted.

## Evidence

- TCP conversations.
- Stream carrying the shell.
- Connection command and redacted output.

## Lessons learned

- Shells without TLS are trivial to reconstruct.
- High ports do not imply encryption.
- Timeline correlation separates sessions.

## Mitigations and detection

- Encrypt all traffic and segment the network.
- Detect outbound connections to high ports and `nc`/`bash -i` processes.
- Retain PCAP only as long as needed.

## References

- <https://www.hackthebox.com/challenges/Wrong%20Spooky%20Season>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/wrong-spooky-season/>
