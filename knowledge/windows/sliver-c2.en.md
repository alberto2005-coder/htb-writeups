---
topic: Sliver C2
tags: [windows, sliver, c2, implant, dfir, network, persistence]
---

# Sliver C2

**English** | [🇪🇸 Español](sliver-c2.md)

## Concept

Sliver is a command-and-control framework with implants for Windows, Linux and macOS. Implants can use mTLS, HTTPS, DNS or WireGuard, and run tasks, tunnels and lateral movement. Analysis looks for the binary, embedded configuration, channels and execution artefacts.

## When it applies

- Encrypted C2 traffic to a domain or IP.
- Processes with a legitimate name but no signature.
- Persistence and scheduled tasks.
- Memory or suspicious binary analysis.

## Procedure

1. Isolate the host and preserve memory and disk.
2. Look for anomalous processes, services and tasks.
3. Extract strings, domains, certificates and keys.
4. Correlate connections and beaconing.
5. Identify the implant and its configuration.

```powershell
Get-Process | Where-Object { $_.Path -and -not (Get-AuthenticodeSignature $_.Path).SignerCertificate }
Get-NetTCPConnection -State Established
Get-ScheduledTask | Where-Object { $_.Actions.Execute -match 'AppData|ProgramData|Temp' }
```

## Variants

- mTLS implant with an embedded certificate.
- HTTPS with domain fronting.
- DNS or WireGuard.
- Interactive sessions, tunnels and assembly execution.

## Limitations

- The configuration may be encrypted.
- The binary may be obfuscated or packed.
- The C2 may use legitimate infrastructure.
- Without memory, some context is lost.

## Mitigation and detection

- Sign binaries and allow only known ones.
- Monitor beaconing, certificates and new domains.
- Restrict service and task creation.
- Alert on unsigned processes and periodic outbound connections.

## References

- <https://github.com/BishopFox/sliver>
- <https://attack.mitre.org/techniques/T1071/>
- <https://www.cisa.gov/resources-tools/resources/command-and-control>
