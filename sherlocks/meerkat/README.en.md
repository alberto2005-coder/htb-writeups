---
sherlock: Meerkat
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, suricata, credential-stuffing, cve-2022-25237, bonitasoft, persistence]
---

# Meerkat — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no platform answers.

## Scenario

Forela runs a business process platform (**Bonitasoft BPM**) and suspects compromise. A **PCAP** and the **Suricata alerts JSON** for the window are provided.

## Evidence

```text
meerkat.pcap
meerkat-alerts.json
```

## Investigation

### 1. Alerts first

```bash
jq -r '.alert.signature' meerkat-alerts.json | sort | uniq -c | sort -rn | head
jq 'select(.alert.severity==1)' meerkat-alerts.json | head -40
```

Three families appear: default-user login attempts (`ET WEB_SPECIFIC_APPS Bonitasoft Default User Login Attempt`), the authorization bypass (`ET EXPLOIT Bonitasoft Authorization Bypass M1 (CVE-2022-25237)`) and download traffic to an external paste site.

### 2. Credential stuffing

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.request.uri contains "loginservice"' \
  -T fields -e frame.time -e ip.src -e http.user_agent | head -50
```

Hundreds of `POST /bonita/loginservice` from `python-requests/2.28.1` with **different username/password pairs** from one IP: credential stuffing, not brute force against one account. It ends in a `204`/`200` with session cookies and a valid account.

### 3. CVE-2022-25237

Bonita Web 2021.2 ships a `RestAPIAuthorizationFilter` with an overly broad exclude pattern: appending **`;i18ntranslation`** (or `/../i18ntranslation/`) to the URL reaches privileged endpoints without permission. The PCAP shows `/bonita/API/...` calls returning `200` where `403` was expected.

### 4. Malicious extension and execution

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.request.uri contains "pageUpload"' \
  -T fields -e frame.time -e ip.src -e http.request.uri
```

The actor uploads a ZIP (`rce_api_extension.zip`) through `/bonita/API/pageUpload`, publishes it and calls `/bonita/API/extension/rce?cmd=...`: command execution as the service account. It checks with `whoami` first and deletes the ZIP to cover tracks.

### 5. Persistence

The command is a `wget` to **`pastes.io`**; the downloaded script `curl`s a second paste and **appends it to `/home/ubuntu/.ssh/authorized_keys`**, then restarts `ssh`. That is **T1098.004** (Account Manipulation: SSH Authorized Keys). With the original paste deleted, the Wayback Machine copy recovers it.

## Findings

- Access: credential stuffing against `loginservice` with a valid corporate account.
- Escalation: CVE-2022-25237 to bypass API authorization.
- Execution: extension uploaded through the panel itself (`pageUpload` → `extension/rce`).
- Persistence: public key in `ubuntu`'s `authorized_keys`.

## Lessons

- Alerts give the "what"; the PCAP gives the "how" and "when".
- Telling stuffing (varied users) from spraying (same password) changes the response.
- An endpoint that uploads plugins is code execution by design: restrict it.
- Mitigation: MFA and rate limiting on the API, patch Bonita, allowlist extensions, monitor `authorized_keys`.
