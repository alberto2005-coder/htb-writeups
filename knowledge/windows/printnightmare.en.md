---
topic: PrintNightmare y el spooler de Windows
tags: [windows, printnightmare, spooler, cve-2021-34527, privilege-escalation]
---

# PrintNightmare and the Windows Spooler

**English** | [🇪🇸 Español](printnightmare.md)

## Concept

PrintNightmare covers Print Spooler flaws that allow a driver or DLL to be loaded with elevated privileges. RCE and LPE variants affect unpatched systems and permissive configurations.

## When it applies

- `Spooler` running on a server or workstation.
- Valid credentials for a user.
- Windows versions older than the 2021 patches.

## Procedure

1. Check the service and patches.
2. Enumerate whether the user can add drivers.
3. Prepare a driver DLL.
4. Load it with a compatible tool.
5. Verify execution as SYSTEM.

```powershell
Get-Service Spooler
whoami /priv
```

## Variants

- Remote RCE against the spooler.
- LPE with `AddPrinterDriver`.
- `Point and Print` abuse with a controlled server.

## Limitations

- Patching or disabling the spooler blocks the attack.
- Credentials or local access are required.
- EDR may detect driver loading.

## Mitigation

- Apply the 2021 patches.
- Disable the spooler when not printing.
- Restrict `Point and Print` and drivers.
- Audit driver installation.

## Detection

- Unexpected driver creation.
- `spoolsv.exe` loading DLLs from user paths.
- Spooler events 808/316.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-34527>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34527>
- <https://attack.mitre.org/techniques/T1068/>
