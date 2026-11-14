---
sherlock: Origins
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, ftp, brute-force, s3, data-exfiltration]
---

# Origins — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A company detects anomalous access to its FTP server. A network capture is provided, and the analyst must identify the attack source, compromised credentials, stolen files and later impact.

## Evidence

- `capture.pcap` with FTP and other traffic.
- No disk image or server logs.
- The capture contains the credentials and transfers.

```bash
capinfos capture.pcap
tshark -r capture.pcap -Y ftp -T fields -e ip.src -e ip.dst -e ftp.request.command -e ftp.request.arg
```

## Investigation

### 1. Inventory and triage

Review conversations and protocols. An external host sends a high volume of FTP login attempts in seconds; the pattern is brute force, not normal browsing.

- Attacker IP: `<ATTACKER_IP>`.
- Service: FTP on port 21.
- Time window: `<START>` to `<END>`.
- Server banner/version: visible in the response.

### 2. Credentials and access

Filter `230 Login successful` responses. The first valid login marks the end of brute force. Follow the stream to see the username and password used.

```bash
tshark -r capture.pcap -Y 'ftp.response.code == 230' -T fields -e frame.time -e ip.src -e ftp.request.arg
```

Redact the password; record only the username.

### 3. Exfiltration

After login, the attacker lists directories and downloads files with `RETR`. Extract FTP-DATA objects from Wireshark (`File → Export Objects → FTP-DATA`).

```bash
tshark -r capture.pcap -Y 'ftp.request.command == "RETR"' -T fields -e ftp.request.arg
```

The files contain:

- `s3_buckets.txt` with links to 2022 and 2023 buckets.
- `Maintenance-Notice.pdf` with a backup-server password.
- A contact email for requesting access.

## Conclusions

- Initial access was FTP brute force.
- Inventories and internal documentation were downloaded.
- The S3 buckets were exposed and one held historical data.
- The contact email is a likely phishing target.

## Lessons

- FTP without attempt limits enables brute force.
- Maintenance files should not contain passwords.
- A misconfigured S3 bucket amplifies the impact of an FTP credential.

## References

- <https://www.hackthebox.com/sherlocks/Origins>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://attack.mitre.org/techniques/T1048/>
- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html>
