---
topic: Screensaver persistence
tags: [windows, persistence, screensaver, scr, registry, run-key]
---

# Screensaver persistence

**English** | [🇪🇸 Español](screensaver-persistence.md)

## Concept

Windows runs the configured screensaver when the machine is idle. If an attacker places a malicious `.scr` and changes the screensaver setting or a `Run` entry, the program executes when the session locks or the user logs in.

## When it applies

- `HKCU\Control Panel\Desktop` keys with `SCRNSAVE.EXE`.
- `Run` entries pointing to a `.scr` under `AppData`.
- Unsigned `.scr` files in user paths.
- Machines with permissive screensaver policies.

## Procedure

1. Review the screensaver setting in the registry.
2. Locate the `.scr` file and check its signature.
3. Review `Run`, `RunOnce` and scheduled tasks.
4. Analyze the binary and its C2.
5. Correlate with logon or lock time.

```powershell
Get-ItemProperty 'HKCU:\Control Panel\Desktop' -Name SCRNSAVE.EXE
Get-ChildItem "$env:APPDATA" -Recurse -Filter *.scr
```

## Variants

- `SCRNSAVE.EXE` pointing into `AppData`.
- `Run` entry with a `.scr`.
- Screensaver policy running a user binary.
- Replacing a legitimate screensaver.
- Execution at session lock.

## Limitations

- The screensaver must be enabled.
- The path must be accessible to the user.
- Some EDR blocks `.scr` from `AppData`.
- Execution depends on idleness or lock.

## Mitigation and detection

- Restrict screensavers to signed system paths.
- Monitor changes under `Control Panel\Desktop` and `Run` entries.
- Block `.scr` execution from user profiles.
- Alert on `.scr` processes with network connections.

## References

- <https://attack.mitre.org/techniques/T1546/002/>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://learn.microsoft.com/en-us/windows/win32/controls/about-screen-savers>
- <https://www.microsoft.com/en-us/security/blog/>
