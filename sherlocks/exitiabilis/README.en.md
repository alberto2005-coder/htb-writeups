---
sherlock: Exitiabilis
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, elk, vpn, siem]
---

# Exitiabilis — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation note; no literal platform answers.

## Scenario

A company's SOC detected anomalous activity in its Windows environment. A **HELK** (hunting-oriented ELK) with endpoint telemetry, Windows events and VPN logs is provided. The hypothesis is that a legitimate remote access path, Cisco AnyConnect, was used as the entry point and the attacker moved laterally from there. The task is to reconstruct access, execution and persistence.

## Evidence

- HELK/Kibana indices with Windows and Sysmon events.
- Cisco AnyConnect VPN authentication logs.
- Security events from the DC and affected hosts.
- Processes, services and network connections within the incident window.

```bash
# Export the relevant indices from Kibana/Elasticsearch
curl -s 'http://<HELK>:9200/_cat/indices?v'
```

Record the time range and time zone before correlating. In a HELK, indices may mix `winlogbeat`, `sysmon` and custom sources.

## Investigation

### 1. Inventory and triage

Identify which users and hosts have events in the window. Start with the VPN, because a successful remote authentication explains how the attacker entered without being onsite.

```text
event.dataset: *vpn* and event.outcome: success
```

Review:

- User, public IP and session start/end time.
- Country or ASN of the IP compared with the user's history.
- AnyConnect device and profile.
- Prior failed attempts and locked accounts.

### 2. Timeline

Cross three sources:

1. **VPN:** connection time, user, IP and duration.
2. **Windows Security:** 4624 (logon), 4625 (failed logon), 4648 (explicit credentials), 4672 (special privileges).
3. **Sysmon:** process creation (1), network connections (3), service creation (7045) and file changes.

```text
event.code: (4624 or 4625 or 4648 or 4672 or 7045)
```

VPN time is usually UTC; Windows events may be local. Normalise everything to UTC and note the offset. A type 3 or 10 logon from the VPN IP followed by an unusual child process is the first solid correlation.

### 3. Key artifact

The artifact that cracks the case is the post-logon execution chain: an interactive process (`powershell.exe`, `cmd.exe` or a renamed binary) that downloads or runs a tool, plus a service or task created for persistence. In HELK, filter by host and VPN user, not by IP alone, because the IP may be shared.

```text
host.name: <HOST> and user.name: <USER>
```

Review the process tree and compare it with the host baseline. A `svchost.exe` outside `System32`, a service binary in `ProgramData` or a newly created `schtasks` entry are persistence signals.

## Findings

- Initial access was a valid VPN session, likely with compromised or reused credentials.
- After logon, the attacker ran interactive tooling and created persistence.
- IOCs include the VPN public IP, user, destination host and the names/paths of deployed binaries.
- No signed malware does not mean no intrusion: credential abuse and living-off-the-land tools leave log evidence.

## Lessons

- VPN is an identity surface: MFA and device correlation matter as much as the firewall.
- A HELK is only useful if indices have normalised time zones and fields.
- Review the process tree, not just authentication events.
- Persistence through services or scheduled tasks should alert on its own.
