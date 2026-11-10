---
sherlock: Knock Knock
domain: Network Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, password-spray, ftp, port-knocking, ssh, ransomware, osint]
---

# Knock Knock — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

A Forela development server was accidentally exposed to the internet. The team believes it was hardened and cannot explain the entry. A network capture spanning one or two days around the incident is provided; reconstruct the access and what followed.

## Evidence

```text
capture.pcap
```

## Investigation

### 1. Sweep and target

```bash
tshark -r capture.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn | head
```

An external IP probes dozens of ports against an internal one: a scan. The host with the most probed ports is the dev server.

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z conv,tcp | head
```

### 2. FTP brute force

```bash
tshark -r capture.pcap -Y 'ftp' -T fields -e ip.src -e ip.dst -e ftp.request.command -e ftp.request.arg | head -40
```

Many failed `USER`/`PASS` pairs followed by `230 Login successful`: a **password spray** against the exposed service (accounts such as `alonzo.spire`). From there, `LIST` and `RETR` of configuration files, including a `.backup` of `knockd.conf`.

### 3. From FTP to the hidden service

Among the retrieved files is **port-knocking** configuration (`knockd` rules). The knock sequence opens a port the scan never saw:

```text
sequence    = 29999,50234,45087
seq_timeout = 5
command     = /sbin/iptables -A INPUT -s %IP% -p tcp --dport 24456 -j ACCEPT
```

```bash
tshark -r capture.pcap -Y 'tcp.dstport==29999 || tcp.dstport==50234 || tcp.dstport==45087' \
  -T fields -e frame.time -e ip.src -e tcp.dstport
```

After the sequence a `SYN` gets a `SYN/ACK` on **24456**, previously filtered and running **FTP** (tell Wireshark "Decode As → FTP").

### 4. Access, jail and ransomware

- Valid credentials on the newly opened service: successful login and a stable session.
- **chroot escape**: traversal (`../../`) takes the attacker out of the jailed directory into the real system.
- Final payload downloaded with `wget` and executed: **GonnaCry**-style ransomware encrypting the server's files.

The OSINT part of the challenge is solved by looking up the company details visible in the capture (mail, names, calendar) in public sources.

## Findings

- Entry: password spray against an internet-facing FTP (port 21).
- Movement: `knockd.conf` read from FTP; the 29999 → 50234 → 45087 sequence opens 24456, a second, internal FTP.
- Impact: chroot escape and ransomware deployment.

## Lessons

- Security through obscurity (a filtered port) collapses if the configuration sits on a poorly protected FTP.
- A chroot is not a sandbox: with wrong privileges, traversal escapes it.
- Mitigation: no dev services on the internet, MFA, strong passwords, and immutable backups.
