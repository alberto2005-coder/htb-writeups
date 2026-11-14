---
sherlock: CafePoisoning
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, arp-poisoning, dns-spoofing, pcap, persistence, screensaver, malware]
---

# CafePoisoning — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A café network starts redirecting customers to a fake update page. A network capture and a KAPE triage collection from an employee workstation are provided. Reconstruct the attack, persistence and C2 channel.

## Evidence

- `cafe.pcap` with ARP, DNS and HTTP traffic.
- `KAPE/` with registry, prefetch, MFT, browser and user files.
- No memory image.

```bash
capinfos cafe.pcap
find KAPE -maxdepth 2 -type d | sort
```

## Investigation

### 1. Inventory and triage

Review capture protocols. There is a burst of ARP requests and duplicate replies: one host tries to bind the gateway IP to its own MAC.

```bash
tshark -r cafe.pcap -Y arp -T fields -e arp.opcode -e arp.src.proto_ipv4 -e arp.src.hw_mac | sort | uniq -c
```

The number of hosts and duplicate ARP replies bounds the poisoning scope.

### 2. Poisoning and redirection

After ARP spoofing, client DNS traffic goes to the attacker. Forged replies resolve an update domain to a controlled IP.

```bash
tshark -r cafe.pcap -Y 'dns.flags.response == 0' -T fields -e dns.qry.name | sort | uniq -c
tshark -r cafe.pcap -Y 'dns.flags.response == 1' -T fields -e dns.qry.name -e dns.a
```

The domain imitates the software vendor. The client downloads an executable over HTTP.

### 3. Execution and persistence

In the triage, review Prefetch, Amcache and the registry. The executable runs from an updates folder and creates a `Run` entry pointing to a `.scr` screensaver.

```bash
PECmd.exe -d KAPE/C -o out --csv out
RegistryExplorer.exe KAPE/C/Windows/System32/config/SOFTWARE
```

The `...\CurrentVersion\Run` key contains a screensaver path under `AppData`. The mechanism is logon persistence.

### 4. Defenses and C2

The installer runs PowerShell to disable Defender and add exclusions. Later C2 traffic is obfuscated with single-byte XOR; the capture allows recovering the key by trying all 256 values and looking for known strings.

```bash
python3 - <<'PY'
data = open("c2.bin", "rb").read()
for k in range(256):
    out = bytes(b ^ k for b in data)
    if b"http" in out or b"cmd" in out:
        print(k, out[:120])
PY
```

## Conclusions

- Initial access was ARP/DNS poisoning on a shared Wi-Fi network.
- The user downloaded a fake updater from a spoofed domain.
- Persistence uses a `Run` entry with a `.scr`.
- The malware disables Defender and uses single-byte XOR for C2.

## Lessons

- Open networks enable layer-2 attacks.
- A lookalike domain is not legitimacy; verify signature and origin.
- `Run` entries pointing into `AppData` are suspicious.
- Single-byte XOR is obfuscation, not encryption.

## References

- <https://www.hackthebox.com/sherlocks/CafePoisoning>
- <https://attack.mitre.org/techniques/T1557/002/>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://attack.mitre.org/techniques/T1562/001/>
