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

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

The SIEM alerts on a suspicious logon: the **source IP and workstation name do not match**. A network capture from the incident window and the Windows Security log are provided; correlate them and explain what happened.

## Evidence

```text
Reaper/ntlmrelay.pcapng
Reaper/Security.evtx
```

## Investigation

### 1. Explaining the alert

Windows records the client-declared `Workstation Name` and the arriving IP in event **4624**. An attacker relaying authentication can send one machine's name from another IP: that is what trips the rule.

```powershell
Get-WinEvent -Path .\Security.evtx -FilterXPath "*[System[EventID=4624]]" |
  Select-Object TimeCreated, @{n='msg';e={$_.Message}} | Format-List
```

Note `LogonType` (3 = network), user, `Workstation Name`, IP and time.

### 2. The typo that opens the door

The PCAP shows the victim mistyping a share path (`\\FORELA-WKSTN00X\...`). Since the name does not exist, the host asks the whole network over **LLMNR/NBNS**:

```bash
tshark -r ntlmrelay.pcapng -Y 'llmnr || nbns' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.name -e nbns.name
```

The attacker answers and the victim authenticates to them.

### 3. The relay

With `ntlmrelayx` the attacker does not keep the hash: they **relay** it to another machine where that user has more rights. The PCAP shows the outbound SMB session and the Security log shows the result:

- **4624** type 3 with the victim user, but from the attacker's IP
- **5140** share access (`\\*\share`) on the target host

```bash
tshark -r ntlmrelay.pcapng -Y 'smb2' -T fields -e ip.src -e ip.dst -e smb2.filename | sort -u
```

### 4. Timeline

Join: name typo → LLMNR query → attacker answer → SMB auth to the attacker → 4624/5140 on the target. Order and seconds between steps are the proof; a lone 4624 proves nothing.

## Findings

- Vector: LLMNR/NBT-NS poisoning after a mistyped name.
- Technique: **NTLM relay** to another workstation, not cracking.
- Proof: `Workstation Name` vs IP mismatch in 4624, plus 5140 on the target.

## Lessons

- A mistyped name is enough for a user to hand over their authentication.
- Relay is detected by crossing network and logs: the captured hash never appears, because it is forwarded, not captured.
- Mitigation: disable LLMNR/NBT-NS, require SMB signing and LDAP channel binding, and segment workstations from each other.
