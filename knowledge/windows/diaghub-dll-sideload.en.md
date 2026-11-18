---
topic: DiagHub — loading a DLL as SYSTEM
tags: [windows, diaghub, dll, arbitrary-write, system, privesc, hackback]
---

# DiagHub — loading a DLL as SYSTEM

[🌐 Español](diaghub-dll-sideload.md) | **English**

## Idea

DiagHub is the Microsoft Diagnostics Hub Standard Collector service, running as SYSTEM and invoked over COM. When its object is instantiated, the service loads a library from `C:\Windows\System32`. If an attacker can write to that directory, a DLL with the expected name can be dropped and loaded with SYSTEM rights. On Hackback a service writing logs as SYSTEM allowed placing the file, and DiagHub completed the escalation.

## When it applies

- `DiagnosticsHub.StandardCollector.Service` exists and is running.
- Arbitrary write as SYSTEM or administrator into `System32` is available.
- The service loads DLLs from a fixed path without signature validation.
- A prior mechanism allows writing the file (a service with a redirectable log, a task, an installer).

## Procedure

1. Enumerate the service and its configuration.
2. Confirm it can be invoked over COM without privileges.
3. Obtain write access to `System32` (on Hackback, by redirecting `UserLogger`'s log).
4. Build a DLL that runs a command when loaded.
5. Place it under the name the service expects.
6. Invoke the COM object and confirm execution as SYSTEM.

## Commands

```powershell
sc qc DiagnosticsHub.StandardCollector.Service
sc query DiagnosticsHub.StandardCollector.Service
reg query "HKLM\SYSTEM\CurrentControlSet\Services\DiagnosticsHub.StandardCollector.Service"
```

```powershell
$type = [Type]::GetTypeFromCLSID('<CLSID>')
$obj = [Activator]::CreateInstance($type)
```

```c
// Minimal DLL: run a command from DllMain
BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID r) {
    if (reason == DLL_PROCESS_ATTACH) system("cmd.exe /c <COMMAND>");
    return TRUE;
}
```

## Variants

- Use `rundll32` or a custom service to force loading if COM fails.
- If `System32` is not writable, look for a configurable load path.
- Combine it with a service writing as SYSTEM to obtain the file.
- Use a signed DLL if the service validates signatures.

## Limitations

- Writing to a protected directory is required, usually the hard step.
- Windows and service versions may change the path or name.
- An EDR may block unsigned DLL loads.
- The DLL runs once per instance; keep it idempotent.

## Mitigation

- Restrict writes to `System32` and audit service ACLs.
- Apply WDAC or AppLocker to unsigned DLLs.
- Review services that log to controllable paths.
- Update Windows and monitor file creation in `System32`.
- Use managed service accounts and least privilege.

## Detection

- DLL creation in `System32` outside an update.
- DiagHub service start followed by child processes.
- Event 7045 service installs and `ImagePath` changes.
- Unsigned DLL loads from SYSTEM processes.

## References

- [Microsoft — Diagnostics Hub](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/)
- [MITRE ATT&CK — DLL Side-Loading](https://attack.mitre.org/techniques/T1574/002/)
- [0xdf — Hackback](https://0xdf.gitlab.io/2019/07/06/htb-hackback.html)
- [Hackback writeup](../../machines/windows/hackback/README.en.md)
