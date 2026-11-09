---
sherlock: CrownJewel-1
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, dcsync, golden-ticket, domain-admin]
---

# CrownJewel-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A Windows domain shows administrative activity nobody recognises. Telemetry from the domain controllers and a couple of member servers is provided; the goal is to establish how domain control was obtained and which accounts are compromised.

## Evidence

- Security logs from the DC and member servers.
- Directory replication events (4662) and service access records.
- Endpoint artefacts from the hosts involved.

## Investigation

### 1. Unauthorised replication

`4662` with the replication GUID (`1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`) from a non-machine account points to **DCSync**:

```bash
grep "4662" Security.evtx | grep -i "1131f6aa" | head
```

Identify the account that requested replication and the host it came from.

### 2. The step before

DCSync is never first. Look for the granting of `DS-Replication-Get-Changes` in ACL change logs, and for how that account was compromised: phishing, password reuse, or an exposed service.

### 3. Persistence

```bash
grep "4769" Security.evtx | grep -i "krbtgt" | head
```

`krbtgt` tickets requested from non-DC hosts suggest a **golden ticket**. A `4768` without a preceding `4624` and atypical `Ticket Options` strengthens it.

## Findings

- Escalation to domain control through directory replication with a compromised account.
- Likely golden-ticket persistence: `krbtgt` must be rotated twice.
- Scope covers every domain secret, not just the analysed hosts.

## Lessons

- `4662` plus the replication GUID is the cleanest DCSync evidence.
- A golden ticket leaves no `4624`: that is why `4768`/`4769` on the DC matter.
- Response to domain compromise starts with `krbtgt`, not the endpoint.
