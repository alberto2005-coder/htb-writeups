---
topic: SeLoadDriverPrivilege escalation
tags: [windows, privesc, driver, seloaddriverprivilege, capcom, edr]
---

# SeLoadDriverPrivilege escalation

**English** | [🇪🇸 Español](seloaddriver-privesc.md)

## Concept

`SeLoadDriverPrivilege` allows loading and unloading drivers. A user with this privilege can load a signed but vulnerable driver and use it to run kernel-mode code, bypass system protections and gain `NT AUTHORITY\SYSTEM`.

## When it applies

- Service accounts with `SeLoadDriverPrivilege` enabled.
- Groups such as `Print Operators` or `Server Operators` in legacy configurations.
- Systems without vulnerable-driver blocking.
- Ability to write to the registry and `%TEMP%`.

## Procedure

1. Check privileges with `whoami /priv`.
2. Check whether the privilege is enabled or can be enabled.
3. Identify an available signed, vulnerable driver.
4. Register the driver as a service and load it.
5. Perform the privileged action and clean up the service.

```powershell
whoami /priv
reg add HKLM\System\CurrentControlSet\Services\<NAME> /v ImagePath /t REG_EXPAND_SZ /d "\??\C:\<PATH>\<DRIVER>.sys" /f
```

## Variants

- Legacy driver such as Capcom.sys to disable protection.
- Vulnerable virtual-hardware or monitoring driver.
- Load from a user path with a controlled `ImagePath`.
- Reuse an existing service pointing at the driver.

## Limitations

- The privilege must be present and enableable.
- Windows may block vulnerable drivers via HVCI or blocklists.
- The driver must match the OS version and architecture.
- Loading generates events and may require a reboot.

## Mitigation and detection

- Remove `SeLoadDriverPrivilege` from non-admin accounts.
- Apply vulnerable-driver blocklists and HVCI.
- Audit service creation and driver loads.
- Alert on `reg add` under `CurrentControlSet\Services` and drivers from `%TEMP%`.

## References

- <https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers>
- <https://attack.mitre.org/techniques/T1068/>
- <https://github.com/kkent030315/evil-mhyprot-cli>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
