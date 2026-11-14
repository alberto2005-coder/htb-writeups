---
topic: Windows — C2 channel over ICMP
tags: [windows, icmp, c2, tunneling, egress]
---

# Windows — C2 channel over ICMP

[🌐 Español](icmp-c2.md) | **English**

## Concept

ICMP is often allowed even when HTTP egress is filtered. A client and server can encapsulate commands and output in echo request/reply packets to keep a control channel.

## When it applies

- ICMP egress allowed while HTTP is restricted.
- A Windows host with `ping.exe` or PowerShell.
- Flat networks without ICMP inspection.

## Procedure

1. Prepare an ICMP listener on the attacker side.
2. Run the client on the victim.
3. Send commands and receive output.
4. Encode data to evade filters.
5. Keep the channel alive with keepalives.

## Commands

```powershell
ping -n 1 <ATTACKER>
# ICMP client: encapsulates output in the echo payload
```

## Variants

- Combined DNS/ICMP tunnels.
- PowerShell with `New-Object System.Net.NetworkInformation.Ping`.
- ICMPv6.

## Limitations

- ICMP may be blocked by the firewall.
- Payload size is limited.
- IDSs detect anomalous patterns.

## Mitigation

- Block unnecessary outbound ICMP.
- Inspect and limit packet size.
- Segment the network and monitor egress.

## Detection

- Echo requests with large or repetitive payloads.
- ICMP traffic to uninventoried external hosts.

## References

- <https://attack.mitre.org/techniques/T1095/>
- <https://github.com/bdamele/icmpsh>
