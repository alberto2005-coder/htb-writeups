---
sherlock: Reaper
domain: DFIR / Active Directory
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, ntlm-relay, llmnr, pcap, security-log, event-4624, event-5140]
---

# Reaper — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method notes; no platform answers.

## Scenario

The SIEM alerts on a suspicious logon: the **IP and the source workstation name do not match**. You get the network capture from that window and the Windows Security log; correlate them and explain what happened.

## Evidence

```text
Reaper/ntlmrelay.pcapng
Reaper/Security.evtx
```

## Investigation

### 1. Explaining the alert

Windows records in event **4624** the `Workstation Name` the client claims and the IP it comes from. An attacker **relaying** an authentication can send one machine's name while connecting from another IP: that is the mismatch.

```bash
EvtxECmd -f Security.evtx --csv out --csvf sec.csv
```

Filter the CSV on `EventId=4624` and note `LogonType` (3 = network), user, `WorkstationName`, IP and time (UTC).

### 2. The typo that opens the door

The capture shows the victim mistyping a share name. Since the name does not exist, the host asks the whole segment over **LLMNR/NBT-NS**:

```bash
tshark -r ntlmrelay.pcapng -Y 'llmnr || nbns' \
  -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.name -e nbns.name
```

A host on the same segment answers and the victim authenticates to it.

### 3. The relay

The SMB stream carries **NTLMSSP**: `NEGOTIATE`, the attacker's `CHALLENGE`, the victim's `AUTHENTICATE`. The attacker does not keep the hash: it **forwards** it to another machine where that user holds more privileges.

```bash
tshark -r ntlmrelay.pcapng -Y 'ntlmssp' -T fields -e ip.src -e ip.dst | sort -u
tshark -r ntlmrelay.pcapng -Y 'smb2' -T fields -e ip.src -e ip.dst -e smb2.filename | sort -u
```

In the Security log, the outcome:

- **4624** type 3 for the victim's account, but from the attacker's IP.
- **5140** naming the share that was accessed; here `\\*\IPC$`, the usual channel for enumeration after a relay.

### 4. Timeline

Join them: typo → LLMNR query → attacker's answer → SMB authentication to the attacker → 4624/5140 on the target. Order and the seconds between steps are the proof; a lone 4624 proves no relay.

## Findings

- Vector: **LLMNR/NBT-NS** poisoning after a mistyped name.
- Technique: **NTLM relay** against another workstation, not cracking.
- Proof: the `Workstation Name`/IP mismatch in 4624, plus 5140 on the target.

## Lessons

- A single typo is enough for a user to hand over their authentication.
- Relay detection crosses network and log: there is no hash to crack because the hash is forwarded.
- `EvtxECmd` to CSV plus `jq`/grep beats opening the viewer for one question.
- Mitigation: disable LLMNR/NBT-NS, require SMB signing and LDAP channel binding, and segment workstations from each other.
