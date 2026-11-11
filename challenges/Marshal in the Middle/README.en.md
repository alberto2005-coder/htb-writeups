---
challenge: Marshal in the Middle
category: Challenge
type: Forensics
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, tls, zeek, exfiltration, wireshark]
---

# Marshal in the Middle — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to the historical challenge index and public writeups; not verified with an HTB session.
> No flags or real personal data.

## TL;DR

A ZIP provides eight **Zeek** logs, `bundle.pem`, `secrets.log` and a PCAP from a compromised web server. `dns.log` identifies the attacker host; HTTPS is decrypted in Wireshark with the session key and certificate. Inside there is exfiltration through `POST /api/api_post.php`: first `/etc/passwd`, then `/etc/shadow`, and finally a dump with card data and the challenge marker.

## Statement and surface

- Category **Forensics**, difficulty **Medium**.
- Delivered: `Marshal in the Middle.zip` (usual password `hackthebox`).
- Contents: Zeek logs (`conn.log`, `dns.log`, `http.log`, `ssl.log`, etc.), `bundle.pem`, `secrets.log` and `chalcap.pcapng`.
- The question is whether data was stolen and what it was; there is no service to exploit.

## Recon

```bash
sha256sum 'Marshal in the Middle.zip'
unzip -P hackthebox 'Marshal in the Middle.zip' -d marshal/
ls -la marshal/
capinfos marshal/chalcap.pcapng
```

Zeek logs show the conversation without opening the PCAP:

```bash
cat marshal/dns.log | zeek-cut id.orig_h id.resp_h query | sort -u | head -40
cat marshal/conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto | sort | uniq -c | sort -nr | head
```

Suspicious activity comes from an internal host to a web server and a Pastebin-style service. The attacker and compromised server IPs are confirmed by correlating `dns.log`, `conn.log` and `http.log`.

## Root cause

The web server accepts and executes a `POST` to `/api/api_post.php` without authentication or output controls. The attacker uses it as an exfiltration channel: system files and a database dump are sent to an external service. Traffic is **HTTPS**, but the challenge supplies the session key (`secrets.log`) and certificate chain (`bundle.pem`), so encryption does not protect the evidence.

## Exploitation

### Decrypt TLS

In Wireshark:

1. `Edit → Preferences → Protocols → TLS`.
2. Under **(Pre)-Master-Secret log filename**, select `secrets.log`.
3. In the **RSA keys list**, add `bundle.pem`.
4. Apply and open `chalcap.pcapng`.

The stream decrypts after the `Server Hello`. The frames documented in the writeups are:

| Frame | Content |
|---:|---|
| 5666 | start of the decrypted stream |
| 5725 | `POST` with `/etc/passwd` |
| 7039 | `POST` with `/etc/shadow` |
| 9887 | final dump with card data and the challenge marker |

```bash
tshark -r marshal/chalcap.pcapng -Y 'http.request.method == "POST"' \
  -T fields -e frame.number -e ip.src -e http.request.uri
```

No brute force is needed: the key is in the supplied material. If `secrets.log` does not cover a session, `bundle.pem` only validates the chain; it cannot decrypt without the private key.

### Export HTTP objects

The quickest route is `File → Export Objects → HTTP → Save All`, then search the objects for the challenge marker:

```bash
mkdir -p http_objects
# save the objects from Wireshark into http_objects/
grep -RIn 'HTB{' http_objects/ | head
```

Wireshark can also filter `http.file_data contains "HTB"`; the object is `api_post(4).php` in most writeups. Its content is the exfiltrated dump, not a server file.

## Evidence

- `dns.log`/`conn.log` with the internal host and external destination.
- `secrets.log` and `bundle.pem` loaded in Wireshark.
- Frames 5725, 7039 and 9887 with the `POST`s.
- Exported HTTP objects, challenge marker redacted.
- No flags or real card data.

## Lessons learned

- **HTTPS is not confidentiality if the session key is in the same ZIP**: evidence and key travel together.
- Zeek logs lead to the relevant flow without opening the PCAP; the PCAP is then used to decrypt and read.
- `Export Objects → HTTP` rebuilds `POST` bodies without following the stream by hand.
- Frame 9887 is the target; the earlier ones are intermediate steps (`passwd`, `shadow`).
- An exfiltration channel can be a legitimate API on the compromised server.

## Mitigations and detection

- Do not store TLS session keys next to production captures; separate evidence and secrets.
- Authenticate `/api/api_post.php`, validate body size and type, and restrict output to allowed domains.
- Detection: anomalous `POST`s to internal APIs, large transfers from web servers, connections to Pastebin/paste services and reads of `/etc/passwd` or `/etc/shadow`.
- MITRE: T1041 (exfiltration over C2 channel), T1048 (exfiltration over alternative protocol), T1071.001 (HTTP).
- References: Justus Perlwitz and Phoenix Computing Solutions writeups; Zeek and Wireshark TLS documentation.

## References

- <https://www.justus.pw/writeups/hack-the-box-challenges/marshal_in_the_middle.html>
- <https://www.phoenix-comp.com/HTB/Easy/Marshal-in-the-Middle>
- <https://jebidiah-anthony.github.io/chals/htb/challenges.html>
