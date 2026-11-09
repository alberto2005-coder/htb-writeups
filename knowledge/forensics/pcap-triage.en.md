---
title: PCAP triage — from capture to evidence
tags: [forensics, pcap, wireshark, tshark, dfir]
---

# PCAP triage

**English** | [🇪🇸 Español](pcap-triage.md)

## 1. Inventory before opening

```bash
capinfos capture.pcapng
tshark -r capture.pcapng -q -z io,phs
```

`io,phs` prints the protocol hierarchy: if HTTP, DNS, SMB or TLS show up, you know where to look. Then conversations and endpoints:

```bash
tshark -r capture.pcapng -q -z conv,tcp
tshark -r capture.pcapng -q -z endpoints,ip
```

## 2. Cleartext HTTP

```bash
tshark -r capture.pcapng --export-objects http,out/
tshark -r capture.pcapng -Y 'http.request' -T fields -e http.host -e http.request.uri | sort -u
tshark -r capture.pcapng -Y 'http.request.method=="POST"' -T fields -e http.file_data | head
```

Credentials and flags usually sit in `application/x-www-form-urlencoded` POSTs or in basic auth (`Authorization: Basic`). To follow a conversation:

```bash
tshark -r capture.pcapng -q -z follow,tcp,ascii,<stream>
```

## 3. DNS and exfiltration

```bash
tshark -r capture.pcapng -Y dns -T fields -e dns.qry.name | sort -u | head -50
```

Long random subdomains mean a DNS tunnel: concatenate labels, decode base32/base64url and sort by time (`-e frame.time`). `dnscat2` and `iodine` have recognisable length and alphabet signatures.

## 4. Other protocols that pay off

- **SMB/NTLM**: `-Y ntlmssp` shows the `NTLMSSP_AUTH` with user and domain; `-Y smb2` reveals files and paths.
- **FTP**: `-Y ftp` leaves user, password and `RETR`.
- **USB HID**: `-Y 'usb.capdata'` with the key map; rebuild keystrokes (`usbhid-dump` does not work on a pcap).
- **TLS**: no key, no content; look for `ClientHello` SNI and cleartext certificates.
- **ICMP/DNS tunnelling**: anomalous sizes and many packets to one destination.

## 5. Correlate and answer

1. Fix the incident **time window** (`frame.time`).
2. Identify **who talked to whom** (conversations, endpoints).
3. Extract the **artefact** (file, credential, command) and hash it.
4. Cross-check host logs (Sysmon, auth.log) to confirm execution.

```bash
sha256sum out/*
```

## 6. Typical errors

- **`tshark` sees no HTTP** → traffic uses 8080/8443 or TLS: adjust filters and ports.
- **`--export-objects` extracts garbage** → the stream is compressed (`Content-Encoding: gzip`); decompress the object.
- **Many DNS names, none useful** → sort by length and time, not alphabetically.
- **Handshake missing** → capture starts mid-session; TLS cannot be decrypted.
- **`capinfos` fails** → truncated file; try `editcap -F pcap` or `tcpdump -r`.

## 7. Detection and mitigation

- PCAP retention at the perimeter and on critical endpoints; synchronised clocks.
- Alerts for DNS tunnels (label length, volume, entropy) and cleartext HTTP credentials.
- Segmentation so internal traffic is not visible from a single point.
- In DFIR, document exact filters and commands: reproducibility is the evidence.

MITRE: T1048, T1071.004, T1040.
