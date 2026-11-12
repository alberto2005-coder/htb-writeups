---
sherlock: Recollection
difficulty: Easy
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, memory, volatility, windows, powershell, malware]
---

# Recollection — Hack The Box Sherlock

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (4 Apr 2024). Reference writeup; not played on this profile.
> No flags, hashes or real C2 strings.

## TL;DR

The challenge provides a Windows memory dump (`recollection.bin`) inside `recollection.zip`. Volatility 3 reconstructs processes, command lines, connections and injected memory. Malicious activity starts with obfuscated PowerShell that downloads and runs a payload, followed by injection into a system process. The flag lives in process memory or a recovered file.

## Setup

```bash
unzip recollection.zip
file recollection.bin
python3 -m venv venv && source venv/bin/activate
pip install volatility3
vol -f recollection.bin windows.info
```

`windows.info` confirms the version, build and symbol scheme. If Volatility cannot find symbols, download them from Microsoft's symbol server or use the symbol pack bundled with the Sherlock distribution.

## 1. Processes

```bash
vol -f recollection.bin windows.pslist
vol -f recollection.bin windows.pstree
vol -f recollection.bin windows.cmdline
```

What to look for:

- `powershell.exe` with `-enc`, `-nop`, `-w hidden` or `DownloadString`.
- `rundll32.exe`, `regsvr32.exe`, `mshta.exe` as children of Office or the browser.
- A legitimate process name running from `Temp`, `AppData` or `Downloads`.
- A `svchost.exe` whose PPID is not `services.exe`.

```bash
vol -f recollection.bin windows.cmdline | grep -iE 'powershell|rundll32|mshta|regsvr32'
```

## 2. Network

```bash
vol -f recollection.bin windows.netscan
vol -f recollection.bin windows.netstat
```

Correlate PID, remote IP and port. A user process connecting to an external 443/8443 port with no browser association is suspicious. Record the IP as `<C2_IP>`; do not publish the real one.

## 3. Injected memory

```bash
vol -f recollection.bin windows.malfind
vol -f recollection.bin windows.vadinfo --pid <PID>
```

`malfind` flags `PAGE_EXECUTE_READWRITE` regions with no backing file and an MZ header. Dump the region:

```bash
vol -f recollection.bin windows.malfind --dump --pid <PID>
```

Hash the dump and search strings:

```bash
strings -a <dump>.dmp | grep -iE 'http|powershell|cmd|flag|HTB'
```

## 4. Files and registry

```bash
vol -f recollection.bin windows.filescan | grep -iE 'temp|download|\.ps1|\.exe'
vol -f recollection.bin windows.dumpfiles --virtaddr <OFFSET>
vol -f recollection.bin windows.registry.hivelist
```

- Recover PowerShell scripts and executables from `Temp`.
- `windows.hashdump` can extract local hashes; do not publish them.
- `windows.registry.printkey` reads Run keys and services.

## 5. Timeline

| Step | Evidence |
|---|---|
| Initial execution | `cmdline` with encoded PowerShell |
| Download | `netscan` and script strings |
| Injection | `malfind` in a system process |
| Persistence | Run key or service in the registry |
| Flag | Process memory or dumped file |

## Lessons learned

- In memory, the command line matters more than the process name.
- `malfind` only flags suspicious regions; confirmation comes from dumping and reading strings.
- A `svchost.exe` with an external connection and an odd PPID is a strong lead.
- Scripts in `Temp` often contain the download URL and payload path.
- Normalise time: Volatility works in UTC.

## Mitigations and detection

- Enable PowerShell logging (4104) and block `-enc` domain-wide unless approved.
- Alert on user processes with outbound connections and on endpoint `malfind` hits.
- Use AMSI and behavioural rules for injection.
- Detection: PowerShell with `DownloadString`, `rundll32` from Office, `svchost` with an anomalous PPID and RWX regions.
- Isolate the host and capture memory before rebooting.

MITRE: T1059.001, T1105, T1055, T1547.001.

## References

- <https://dev.crollins.io/recollection>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1055/>
