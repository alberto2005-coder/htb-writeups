---
title: Volatility 3 — Windows memory analysis
tags: [forensics, memory, volatility, windows, dfir, malware]
---

# Volatility 3: reading memory without booting the host

**English** | [🇪🇸 Español](volatility-memory.md)

## 1. Before analysis

- **Integrity**: hash the dump with SHA-256 and work on a copy. Record the acquisition tool, time and size.
- **Format**: `.raw`, `.mem`, `.vmem`, `.dmp` or a VMware snapshot (`.vmem` + `.vmsn`). The `.vmsn` gives context, not an independent memory image.
- **Symbols**: Volatility 3 downloads them from Microsoft; in an isolated environment use a local symbol pack.

```bash
sha256sum memory.raw
python3 -m venv venv && source venv/bin/activate
pip install volatility3
vol -f memory.raw windows.info
```

If `windows.info` fails, the profile is unidentified or the dump is corrupt. Do not continue with profile-dependent plugins.

## 2. Processes and command lines

```bash
vol -f memory.raw windows.pslist
vol -f memory.raw windows.pstree
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.getsids
```

- Compare `pslist` with `psscan` (terminated or hidden processes).
- An incoherent PPID reveals injection or process hollowing.
- `cmdline` is the richest source: encoded PowerShell, `rundll32`, paths in `Temp`.

```bash
vol -f memory.raw windows.psscan | grep -iE 'powershell|rundll32|svchost'
```

## 3. Network

```bash
vol -f memory.raw windows.netscan
vol -f memory.raw windows.netstat
```

Correlate PID, remote IP, port and state. A user process connecting to an external port with no browser association is suspicious. In an old dump, `netscan` may miss closed connections.

## 4. Injected code

```bash
vol -f memory.raw windows.malfind
vol -f memory.raw windows.vadinfo --pid <PID>
vol -f memory.raw windows.malfind --dump --pid <PID>
```

`malfind` looks for `PAGE_EXECUTE_READWRITE` regions with no backing file and an MZ header. Not all are malicious (JIT, .NET). Confirm by dumping and checking strings, imports and entropy.

```bash
strings -a <dump>.dmp | grep -iE 'http|cmd|powershell|flag'
```

## 5. Files and registry

```bash
vol -f memory.raw windows.filescan | grep -iE 'temp|download|\.ps1|\.exe'
vol -f memory.raw windows.dumpfiles --virtaddr <OFFSET>
vol -f memory.raw windows.registry.hivelist
vol -f memory.raw windows.registry.printkey --key 'Software\Microsoft\Windows\CurrentVersion\Run'
vol -f memory.raw windows.hashdump
```

- `dumpfiles` recovers content if it is still cached.
- `hashdump` extracts local hashes; never publish them.
- Run keys and services show persistence.

## 6. Timeline

```bash
vol -f memory.raw timeliner --output-file timeline.csv
```

It combines processes, files and connections. Normalise to UTC and cross-check with on-disk EVTX/Prefetch. Memory alone does not prove the full sequence.

## 7. Limits and common mistakes

- **Wrong symbols** → empty or wrong plugin output; pin the version.
- **`malfind` as a verdict** → it is a lead, not proof.
- **Partial dump** → a missing process does not mean it never existed.
- **Local time** → convert to UTC before correlating.
- **Published hashes** → never; they are credentials.

## 8. Detection and response

- Capture memory before shutdown or reboot.
- Isolate the host and preserve the dump with a hash.
- Correlate memory with EVTX, Prefetch and network telemetry.
- Document chain of custody and limitations.

MITRE: T1055, T1059.001, T1105, T1547.

## 9. References

- <https://github.com/volatilityfoundation/volatility3>
- <https://volatility3.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1055/>
