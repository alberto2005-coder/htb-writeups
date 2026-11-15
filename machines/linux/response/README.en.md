---
machine: Response
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, hmac, ldap, forensics, pcap]
---

# Response — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The application exposes an SSRF with an HMAC oracle that signs requests to the internal chat. LDAP authentication is redirected to a rogue server to enter as administrator, a cross-protocol request reads FTP files, and a host added to the scanner leaks an SSH key through a certificate-state traversal. A PCAP and Meterpreter core dump allow the root key to be reconstructed.

## Recon

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and `443/tcp` HTTPS.
- Services: Web proxy, internal chat, LDAP, FTP and a host scanner.
- Technologies: SSRF, HMAC, LDAP, TLS, PCAP, Meterpreter and memory analysis.

## Enumeration

- `response.htb` with a proxy accepting URLs.
- Internal chat reachable only from the server network.
- HMAC oracle that signs parameters.
- Scanner processing hosts and certificates.

## Foothold

Build a proxy that uses the SSRF and HMAC oracle to sign and forward requests to the chat. Start a fake LDAP server that answers authentication as administrator; talk to the bot and obtain FTP credentials.

```bash
python3 ssrf_hmac_proxy.py --target http://response.htb --listen 0.0.0.0:8000
python3 rogue_ldap.py --listen 0.0.0.0:389 --user admin
curl -x http://127.0.0.1:8000 http://chat.internal/
```

## Lateral movement

The bot provides FTP credentials, but they are not directly reachable. Send a link that triggers a cross-protocol request and read the FTP files; then register a host so the scanner processes it.

## Privilege escalation

The scanner accepts a certificate whose state contains a traversal; use it to read the next user's SSH key. The PCAP and Meterpreter core dump hold encrypted traffic and the AES key; decrypting it reveals a ZIP with a screenshot and `authorized_keys`, enough to reconstruct root's private key.

```bash
openssl req -new -x509 -nodes -out cert.pem -keyout key.pem \
  -subj '/CN=../../../../home/<USER>/.ssh/id_rsa'
# Submit the certificate to the scanner and collect the leaked key
tshark -r capture.pcap -Y 'tcp.port == 4444'
volatility3 -f core.dmp windows.pslist
# Decrypt the traffic and reconstruct the key from the screenshot and authorized_keys
```

## Evidence

- Signed chat requests and the bot response.
- FTP files read through the cross-protocol request.
- SSH key and root key reconstructed from the ZIP.

## Lessons learned

- An SSRF with valid signatures can cross internal trust boundaries.
- LDAP authentication without server validation enables a rogue LDAP.
- Forensic artifacts (PCAP and core dump) can contain keys and secrets.

## Mitigation and detection

- Validate destinations, resolve DNS safely and block internal ranges.
- Sign with context and expiry; do not expose an HMAC oracle.
- Use LDAPS with strict validation and rotate keys after an intrusion.

## References

- [0xdf — Response](https://0xdf.gitlab.io/2023/02/04/htb-response.html)
- [IppSec — Response](https://www.youtube.com/watch?v=-t1UAvTxB94)
- [Hack The Box — Response](https://app.hackthebox.com/machines/response)
