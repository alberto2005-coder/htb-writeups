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

> **State:** Retired. Methodology notes; no platform answers.

## Scenario

The IDS flags an unauthorised device on the Active Directory VLAN and unusual **LLMNR** traffic. The known victim is `Forela-WKstn002` (`172.17.79.136`). Find the attacker, the spoofed name, the captured hash and whether it cracked.

## Evidence

- `capture.pcap` (partial; the session start is missing).
- Context: victim workstation and `forela.local` domain.

## Investigation

### 1. Who answers

```bash
tshark -r capture.pcap -Y 'llmnr' -T fields -e frame.number -e ip.src -e ip.dst -e llmnr.qry.name
```

The pattern repeats: the victim asks for a name that does not resolve and **`172.17.79.135` answers** — not the DC. `nbns` also shows the attacker's hostname, **`kali`**: an uninventoried device. The user typed `DCC01` instead of `DC01`, so the lookup fell through to LLMNR.

### 2. NTLMv2 capture

```bash
tshark -r capture.pcap -Y 'ntlmssp' -T fields -e frame.number -e ip.src -e ip.dst \
  -e ntlmssp.auth.username -e ntlmssp.ntlmserverchallenge
```

SMB2 carries `NTLMSSP_AUTH` for **`john.deacon`** against the rogue IP, with server challenge **`601019d191f054f1`** and `NTProofStr` `c0cc803a6d9fb5a9082253a04dbd4cd4`. Assemble the hash:

```text
john.deacon::FORELA:601019d191f054f1:c0cc803a6d9fb5a9082253a04dbd4cd4:<blob>
```

### 3. Cracking

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

Mode **5600 (NetNTLMv2)**. The password falls to a dictionary, so the capture had real impact: valid domain credentials.

### 4. Closing

Record the rogue IP (`172.17.79.135`), hostname (`kali`), victim, user, challenge, hash and crack result. The IDS response: disable LLMNR/NBT-NS by GPO, require SMB signing and segment.

## Findings

- Active LLMNR/NBT-NS lets any host on the VLAN spoof name resolution.
- The chain ends in NTLMv2 plus a dictionary: valid credentials.
- An uninventoried device answering LLMNR is the clearest signal.

## Lessons

- In the PCAP, look at who **answers**, not only who asks.
- `hashcat -m 5600` is extremely fast: password strength is the only real defence.
- A user typo (`DCC01`) is the trigger; the mitigation is disabling the protocol, not awareness training.
