---
sherlock: Meerkat
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, suricata, credential-stuffing, cve-2022-25237, persistence]
---

# Meerkat — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

Forela runs a business process platform (Bonitasoft BPM) and suspects it is compromised. A **PCAP** and the **Suricata alerts JSON** for the incident window are provided. Confirm whether there was an intrusion and reconstruct it.

## Evidence

```text
meerkat.pcap
meerkat-alerts.json
```

## Investigation

### 1. Alerts first, packets second

```bash
jq -r '.alert.signature' meerkat-alerts.json | sort | uniq -c | sort -rn
jq 'select(.alert.severity==1)' meerkat-alerts.json | head -40
```

The dominant alert points at the vector: mass attempts against the API login. Record source IP, `timestamp` and `flow_id`, then find that conversation in the PCAP with Wireshark (`ip.addr==... && tcp.port==...`).

### 2. Brute force / credential stuffing

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST"' \
  -T fields -e frame.time -e ip.src -e http.request.uri -e http.user_agent | head -50
```

Hundreds of `POST /bonita/loginservice` with different users and `401`/`403` statuses, followed by a `200` and a session cookie: that is the turning point. Identify the valid account and the exact moment.

### 3. Authorization bypass and malicious extension

Once authenticated, the actor abuses **CVE-2022-25237**: a flaw in the API `options` parameter validation bypasses authorization checks and reaches admin functionality. In the PCAP it shows as requests to `/bonita/API/...` with tampered parameters returning `200` where `403` used to be.

With privileges, they upload their own **extension/page** (a `.zip` with code) that the server deploys and executes:

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.content_type contains "multipart"' \
  -T fields -e frame.time -e ip.src -e http.request.uri -e http.file_data | head
```

## Findings

- Access: credential stuffing against `loginservice` with one valid account.
- Escalation: CVE-2022-25237 to bypass API authorization.
- Execution: malicious extension uploaded through the admin panel itself.

## Lessons

- Suricata alerts give the "what"; the PCAP gives the "how" and "when". Without crossing both, the timeline stays a hypothesis.
- Credential stuffing shows up as volume and account variety from one IP, not as a single payload.
- Mitigation: rate limiting, MFA on the API, patch CVE-2022-25237, and restrict who may upload extensions.
