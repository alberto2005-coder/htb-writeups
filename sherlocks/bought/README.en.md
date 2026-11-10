---
sherlock: BOughT
domain: DFIR / Malware Analysis
difficulty: Hard
platform: Hack The Box
evidence: Memory dump and an AD1 logical image from a second-hand laptop
tools: [Volatility 2, FTK Imager, Ghidra, CyberChef]
state: Active
tags: [dfir, memory, malware, dga, ddos, persistence, t1547.001]
---

# BOughT — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Active. Investigation notes; no platform answers.

## Scenario

A user buys a second-hand laptop and within days the Internet connection turns unstable and the ISP warns about anomalous traffic. The machine's RAM and a logical disk image are provided.

## Evidence

- `memdump.mem`: memory dump.
- `Files.ad1`: AD1 logical image of the filesystem.

```bash
sha256sum memdump.mem Files.ad1
```

## Investigation

### 1. Inventory and triage

Get the memory profile before any plugin:

```bash
vol.py -f memdump.mem imageinfo
```

```text
Suggested Profile(s): Win10x64_19041
```

The capture is from **2023-08-07 21:28:13**. With the profile, the process tree separates the legitimate from the added:

```bash
vol.py -f memdump.mem --profile=Win10x64_19041 pstree
vol.py -f memdump.mem --profile=Win10x64_19041 cmdline
```

A **`SecurityCheck`** process appears with no system path and a command line pointing at the user's startup folder: persistence via `StartUp`, with no service or scheduled task.

### 2. Timeline

The AD1 image is mounted with **FTK Imager** and the binary extracted. Its metadata gives the sample's SHA-256; execution is dated from the image's own `$MFT`.

```text
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\SecurityCheck.exe
```

The binary creates a **`config_m2`** mutex, the identifier used to check whether it is already running: one mutex per family and campaign.

### 3. Key artifact

In Ghidra, the entry function does:

```c
Sleep(900000);              /* 15 minutes */
if (IsDebuggerPresent()) exit(0);
```

The `Sleep` delays dynamic analysis and `IsDebuggerPresent` aborts it when a debugger is attached: two cheap barriers that explain why the malware "does nothing" in a sandbox.

It then builds domains with a **DGA**: five levels of nine characters (`9^5 = 59049` domains per run). Configuration comes from `C:\Windows\win.ini` and commands from `C:\Users\Public\config.ini`, base64-encoded:

```bash
python3 -c "import base64;print(base64.b64decode(open('config.ini').read()))"
```

The active C2 in the capture is `http://cl0lr8.xyz`. The DDoS behaviour is `ping -n 16` plus bursts of 20 GET requests: low volume, but enough for the ISP to notice.

## Findings

- The laptop arrived compromised: persistence sits in the user's `StartUp` folder, not in a system mechanism.
- The binary protects itself with a delay and a debugger check, and uses a 59,049-domain DGA so blocking one domain is useless.
- Configuration lives in two unremarkable paths (`win.ini`, `Public\config.ini`), letting the operator change C2 without recompiling.

## Lessons

- `pstree` + `cmdline` solve more cases than any signature: the process path gives the persistence away.
- A long `Sleep` is not "inactive malware": it is a design decision; read the code, not just 60 seconds of behaviour.
- `IsDebuggerPresent` is bypassed with ScyllaHide or by patching the jump; static analysis avoids the problem.
- A known mutex lets you hunt the same family on other hosts with a simple rule.

## Mitigations and detection

- Monitor writes to any profile's `StartUp` (Sysmon 11) and executions from that path (Sysmon 1).
- Alert on "security"-named processes with no signature and no system path.
- Block resolution of newly registered, low-TTL domains; DGAs are detected by NXDOMAIN volume, not by name.
- Treat `win.ini` and `C:\Users\Public` as anomalous configuration paths in integrity scans.

MITRE: T1547.001 (registry run keys / startup folder), T1498 (network denial of service), T1568.002 (domain generation algorithms), T1497.001 (virtualization/sandbox evasion).

## References

- <https://mwalkowski.com/post/sherlock-bought>
- <https://github.com/volatilityfoundation/volatility>
- <https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns>
