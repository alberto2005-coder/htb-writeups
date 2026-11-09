---
sherlock: Noxious
domain: DFIR / Active Directory
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, llmnr, ntlmv2, responder, hashcat, active-directory]
---

# Noxious — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

The IDS reports a possible rogue device on the Active Directory VLAN and unusual **LLMNR** traffic. LLMNR poisoning is suspected: locate the attacker, the victim, and prove whether the credentials were cracked.

## Evidence

- Partial network capture of the VLAN.
- Victim context (`Forela-WKstn002`).

## Investigation

### 1. Who asks and who answers

In Wireshark:

```text
llmnr
nbns
```

LLMNR and NBT-NS are **local** name resolution: when a host cannot resolve a name via DNS, it asks the whole network. An attacker running Responder answers "that's me" and the victim sends its authentication.

The poisoning signature is an LLMNR/NBT-NS **response** from an IP that is not the legitimate server, followed by SMB traffic to that IP.

### 2. Victim and attacker

```bash
tshark -r capture.pcap -Y 'llmnr' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.name
```

Identify the victim (the asker) and the IP that always answers with the same fake name, which also resolves an offensive hostname over NBNS. That IP is the rogue device.

### 3. NTLMv2 capture

```bash
tshark -r capture.pcap -Y 'ntlmssp' -T fields -e ip.src -e ip.dst -e ntlmssp.auth.username -e ntlmssp.ntlmserverchallenge
```

The SMB exchange carries `NTLMSSP_AUTH` with the victim user and the `ServerChallenge`. Rebuild the hash as `user::domain:challenge:proof:blob` and test whether the password falls:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

If it cracks, impact is real: a domain user's password is in the attacker's hands.

### 4. Wrap-up

Document: rogue IP, fake name, victim, captured user, whether it cracked, and when. The IDS response includes disabling LLMNR/NBT-NS by GPO and requiring SMB signing.

## Findings

- Enabled LLMNR/NBT-NS lets any host on the VLAN impersonate name resolution.
- Poisoning leads to NTLMv2 capture and, with weak passwords, to valid credentials.
- An uninventoried device answering LLMNR is the clearest attack signal.

## Lessons

- Disabling LLMNR and NBT-NS by GPO is the primary mitigation; the rest are patches.
- `hashcat -m 5600` on NTLMv2 is fast: password strength is the only real defence.
- In a PCAP, always look at who **answers** the queries, not just who asks.
