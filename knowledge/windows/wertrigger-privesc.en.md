---
topic: Windows — WerTrigger and privileged DLL loading
tags: [windows, wertrigger, wer, dll, escalation, proper]
---

# Windows — WerTrigger and privileged DLL loading

**English** | [🌐 Español](wertrigger-privesc.md)

## Idea

Windows Error Reporting (WER) runs with elevated privileges when a process crashes. WerTrigger places a file and triggers a fault so WER loads a DLL from a controlled path. With arbitrary write to a path WER searches, this yields SYSTEM execution. On Proper, the `Cleanup` service's arbitrary write was combined with WerTrigger to finish the box.

## When it applies

- Arbitrary write as SYSTEM or to a DLL search path exists.
- WER is enabled and runs with privileges.
- A process crash can be triggered.
- The DLL path is unprotected.

## Procedure

1. Identify an arbitrary write or a DLL search path.
2. Place the malicious DLL with the expected name.
3. Trigger the WER fault.
4. Wait for WER to load the DLL.
5. Confirm execution as SYSTEM.

## Commands

```powershell
# The POC writes phoneinfo.dll to System32 and triggers a WER fault
Copy-Item .\phoneinfo.dll C:\Windows\System32\phoneinfo.dll
```

```text
%LOCALAPPDATA%\Microsoft\Windows\WER\
C:\ProgramData\Microsoft\Windows\WER\
```

## Variants

- Abuse `RegisterWaitForInputIdle` or a controlled crash.
- Combine with a service that restores files as SYSTEM.
- Use a privileged process's DLL search path.
- Use WER to load a signed or legitimately named DLL.
- Chain with `PrintNightmare` or `AlwaysInstallElevated`.

## Limitations

- WER may be disabled by policy.
- The path must be writable and on the DLL search path.
- The DLL must match the process architecture.
- The crash must be reproducible.
- Modern versions apply DLL-loading mitigations.

## Mitigation

- Disable WER on servers or restrict its configuration.
- Protect WER paths and data folders.
- Enforce `SafeDllSearchMode` and absolute paths.
- Review services with arbitrary write.
- Monitor DLL creation in WER paths.

## Detection

- New DLLs under `%LOCALAPPDATA%\Microsoft\Windows\WER` or `C:\ProgramData`.
- `WerFault.exe` loading user DLLs.
- Repeated crashes of the same process.
- DLL writes by privileged services.
- Loading of `phoneinfo.dll` by `WerFault.exe` or unknown binaries.

## References

- [0xdf — Proper](https://0xdf.gitlab.io/2021/08/21/htb-proper.html)
- [GitHub — WerTrigger](https://github.com/sailay1996/WerTrigger)
- [Microsoft — Windows Error Reporting](https://learn.microsoft.com/en-us/windows/win32/wer/windows-error-reporting)
- [Proper writeup](../../machines/windows/proper/README.en.md)
