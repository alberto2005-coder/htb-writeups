---
machine: Laser
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, printer, pjl, grpc, solr, ssh, docker]
---

# Laser — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Two unusual ports: JetDirect (9100) and a gRPC service (9000). An encrypted print job and the in-memory key are extracted from the printer, revealing the Feed Engine specification. A gRPC client performs SSRF against localhost Apache Solr and achieves RCE as `solr`. On the host, `pspy` shows root using `sshpass` into a container; that connection is intercepted and `clear.sh` is controlled to obtain a SUID bash on the host.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,9000,9100 <IP>
python3 /opt/PRET/pret.py <IP> pjl
```

## Enumeration

- 9100 answers PJL and identifies as a LaserCorp printer.
- The queued job is encrypted; `nvram dump` leaks the AES key.
- The decrypted PDF describes Feed Engine v1.0, gRPC and port 9000.

## Initial access

Decrypt the job with AES-CBC (IV in bytes 8-23) and read the PDF, which defines the `Print.Feed` service. Generate the client with `grpc_tools.protoc` and submit a feed URL pointing at Solr on `127.0.0.1:8983`. Enabling the Velocity template loader executes code and yields a shell as `solr`.

## Privilege escalation

`pspy` reveals root using `sshpass` to copy and run `/tmp/clear.sh` inside the `172.18.0.2` container. Enter the container with that password, replace sshd with `socat` forwarding to the host, and prepare a non-writable `clear.sh`; the `scp` fails, but the following `ssh` runs the controlled content and creates a SUID bash on the host.

## Evidence

- Decrypted print job and PDF describing the protocol.
- SSRF request to Solr and shell as `solr`.
- `clear.sh` executed by root and SUID bash on the host.

## Lessons learned

- Printers and industrial services leak memory and credentials.
- gRPC and Protocol Buffers can be reversed from leaked documentation.
- A container holding root credentials is not a boundary when root trusts it.

## Mitigation and detection

- Isolate printers and disable unauthenticated PJL/NVRAM.
- Do not expose Solr or enable Velocity for untrusted users.
- Avoid `sshpass`, shared keys and root-run scripts in `/tmp`.

## References

- [0xdf — Laser](https://0xdf.gitlab.io/2020/12/19/htb-laser.html)
- [IppSec — Laser](https://www.youtube.com/watch?v=vD3jSJlc0ro)
- [Hack The Box — Laser](https://app.hackthebox.com/machines/laser)
