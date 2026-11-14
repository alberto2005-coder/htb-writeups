---
topic: Windows IoT Core and Sirep
tags: [windows, iot, sirep, wdp, registry, credentials, omni]
---

# Windows IoT Core and Sirep

**English** | [🇪🇸 Español](iot-core-sirep.md)

## Concept

Windows IoT Core exposes the Sirep protocol on port 29826 and Windows Device Portal (WDP) on 8080. Sirep allows command execution and file transfer; if unrestricted, an attacker can save registry hives, extract credentials and run code as administrator.

## When it applies

- Devices running Windows IoT Core.
- Ports 29826 and 8080 reachable.
- Default or weak administrator credentials.
- Labs replicating Omni.

## Procedure

1. Enumerate ports and confirm Sirep/WDP.
2. Use SirepRAT to run commands.
3. Save `SAM` and `SYSTEM` with `reg save`.
4. Extract hashes with `secretsdump`.
5. Access WDP and run PowerShell as administrator.

```bash
python3 SirepRAT.py <IP> GetSystemInformationFromDevice
python3 SirepRAT.py <IP> ExecuteCommandWithOutput --return_output --cmd "cmd.exe /c whoami"
```

## Variants

- `reg save HKLM\SAM` and `HKLM\SYSTEM` for offline dumping.
- `Import-Clixml` of stored credentials.
- WDP with default credentials.
- PowerShell execution through the management API.

## Limitations

- Sirep must be enabled and reachable.
- WDP may require authentication.
- Extracted credentials may be rotated.
- The IoT Core version limits available commands.

## Mitigation and detection

- Disable Sirep and WDP outside labs.
- Segment IoT devices and change credentials.
- Restrict ports 29826 and 8080 at the firewall.
- Alert on `reg save`, WDP access and remote commands.

## References

- <https://github.com/SafeBreach-Labs/SirepRAT>
- <https://learn.microsoft.com/en-us/windows/iot/iot-enterprise/develop/device-portal>
- <https://attack.mitre.org/techniques/T1003/002/>
- <https://attack.mitre.org/techniques/T1210/>
