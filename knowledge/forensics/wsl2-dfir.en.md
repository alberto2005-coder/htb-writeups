---
title: WSL2 in DFIR — host artifacts and API capture
tags: [forensics, dfir, wsl2, windows, api-monitor, vhdx]
---

# WSL2 in DFIR: the blind spot, and how to open it

**English** | [🇪🇸 Español](wsl2-dfir.md)

## 1. Why WSL2 is a blind spot

WSL2 runs a real Linux kernel inside a lightweight VM. What happens inside it — ELF processes, shell history, connections, staged files — **produces no Prefetch, no 4688 and no process Sysmon** on the host. Sysmon only sees access to Windows utilities (`/mnt/c/...`, `powershell.exe`).

Practical consequence: an investigator who only looks at Windows artifacts cannot see an attacker working inside the distro.

## 2. Host artifacts

**Registry.** Every registered distro lives under `HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss\<GUID>`:

| Value | Content |
|---|---|
| `BasePath` | filesystem path (default `%LOCALAPPDATA%\Packages\...\LocalState`) |
| `DistributionName` | distro name |
| `Version` | 1 or 2 |
| `DefaultUid` | default UID |

**Disk.** On WSL2, `BasePath` contains `ext4.vhdx`: the entire filesystem. It is the primary evidence.

**Windows execution.** Prefetch for `wsl.exe` and `wslhost.exe`, plus Hyper-V events (`Microsoft-Windows-Hyper-V-VmSwitch-Operational`) showing when the VM started.

## 3. Mounting the disk

With the distro shut down (`wsl --shutdown`), attach it in *bare* mode so it is not mounted automatically:

```powershell
wsl.exe --mount "C:\Users\<USER>\AppData\Local\Packages\<DISTRO>\LocalState\ext4.vhdx" --vhd --bare
```

From another distro, identify the device and mount read-only:

```bash
lsblk
mkdir -p /mnt/evidence
mount -o ro /dev/sdX /mnt/evidence
```

Cross-platform alternative with libguestfs:

```bash
guestmount --add ext4.vhdx --ro -i ./import/
```

With the filesystem mounted, analysis is plain Linux: `~/.bash_history`, `~/.zsh_history`, `/var/log`, `/tmp`, `crontab`, SSH keys, `.gitconfig`, downloaded ELF binaries.

## 4. API capture: seeing what Windows does not log

The technique published by HTB (July 2023) hooks the Win32 APIs WSL2 uses to talk to the kernel: `RtlUnicodeToUTF8N` (string conversion between the Linux side and NT) and `WriteFile` (writes to the pipe/socket handles that carry console and data).

- **API Monitor** saves captures as `.apmx64`. That file **is a ZIP**: unzipping gives one blob per monitored process.
- Blobs are captured memory, not text: `strings` in ASCII and UTF-16LE recovers typed commands, file contents and network responses.
- In a capture, `RtlUnicodeToUTF8N` with a long string followed by `WriteFile` on an outbound handle is the pattern of exfiltration from the distro.

```bash
unzip -o Employee.apmx64 -d employee/
strings -a  employee/* | grep -i "powershell\|cat \|curl\|Invoke-"
strings -el employee/* | head
```

## 5. From guest to host

Bridges worth knowing:

- **`/mnt/c`**: direct access to the Windows disk; an ELF can write into `C:\Users\...` without spawning a Windows child process.
- **Interop**: `powershell.exe`, `cmd.exe` or `wsl.exe` invoked from Linux do create a Windows process; telemetry exists again there.
- **`lsassy`** from the distro: uses `sekurlsa`/`comsvcs` against the host through `powershell.exe` or RPC, so the malicious binary never touches the Windows disk.

## 6. Correlation

```text
Lxss (BasePath + Version 2)
  → wsl.exe Prefetch
  → API capture with RtlUnicodeToUTF8N + WriteFile
  → 4688/4104 only if interop with PowerShell happened
```

The typical Sherlock question — "which API does WSL2 use to write to the pipe?" — is answered by the architecture, not by an event: `WriteFile`.

## 7. Detection and mitigation

- Disable WSL where it is not used (`dism /online /disable-feature /featurename:Microsoft-Windows-Subsystem-Linux`) and restrict installation by policy.
- EDR with WSL visibility (coverage is uneven; never assume the guest is monitored).
- Alert on `wsl.exe` spawned by non-interactive processes, on writes to `LocalState\ext4.vhdx` outside normal use, and on interop into `powershell.exe`.
- During response: shut the distro down, preserve `ext4.vhdx` and the `Lxss` registry, and analyse the VHDX read-only.

MITRE: T1059.004 (Unix shell), T1041, T1567, T1070.
