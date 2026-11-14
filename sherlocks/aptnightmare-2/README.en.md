---
sherlock: APTNightmare-2
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, memory, linux, volatility3, dwarf2json, rootkit, apt]
---

# APTNightmare-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A corporate Linux server rebooted unexpectedly and the response team captured memory before shutting it down. The dump, `System.map` and a generic profile are provided. An actor with root access and stealthy persistence is suspected.

## Evidence

- `memdump.mem` (memory dump).
- `System.map` for the running kernel.
- `profile.json` or a generic profile description.
- No disk image.

```bash
ls -lh memdump.mem System.map
strings -a memdump.mem | grep -m3 'Linux version'
```

## Investigation

### 1. Symbol preparation

Volatility 3 does not recognize the kernel by default. Get the exact banner version and build an ISF (Intermediate Symbol Format) with `dwarf2json`, using `System.map` and, when available, the matching `vmlinux`.

```bash
dwarf2json linux --system-map System.map --elf vmlinux > linux-<VERSION>.json
mkdir -p volatility3/volatility3/symbols/linux
cp linux-<VERSION>.json volatility3/volatility3/symbols/linux/
```

Without `vmlinux`, a kernel from the same build can be used after verifying offsets. A wrong profile yields empty or incorrect results.

### 2. Processes and command line

List processes and rebuild the tree. A `bash` whose PPID is a service and which has an interactive session is suspicious. `linux_bash` recovers the session history.

```bash
vol -f memdump.mem linux_pslist
vol -f memdump.mem linux_pstree
vol -f memdump.mem linux_bash
```

The history shows `sudo su`, followed by discovery commands and a process opening a reverse shell. The legitimate `sudo` binary is used for elevation; there is no exploit.

### 3. Network and persistence

`linux_netscan` shows an outbound connection from a process that should not have network access. Review modules and scheduled tasks to locate persistence.

```bash
vol -f memdump.mem linux_netscan
vol -f memdump.mem linux_lsmod
vol -f memdump.mem linux_enumerate_files | grep -iE 'cron|systemd|rc.local'
```

The actor left a service or task that relaunches the implant after reboot. A module loaded outside the standard path suggests a rootkit.

### 4. Correlation and timeline

Order events by process start time and connections. The sequence is: initial access with credentials, `sudo su`, tool download, reverse shell, persistence and log wiping.

```text
login → sudo su → discovery → download → reverse shell → persistence → log wiping
```

## Conclusions

- The attacker gained root with valid credentials, not a kernel vulnerability.
- Memory reveals the history and the C2 connection.
- Persistence survives reboot through a service or task.
- The rootkit hides some activity, but not all telemetry.

## Lessons

- Without correct symbols, Volatility 3 is unreliable.
- `linux_bash` and `linux_netscan` are fast starting points for Linux memory.
- No disk image does not prevent reconstructing the intrusion.
- A rootkit requires comparison against an external baseline.

## References

- <https://www.hackthebox.com/sherlocks/APTNightmare-2>
- <https://github.com/volatilityfoundation/volatility3>
- <https://github.com/volatilityfoundation/dwarf2json>
- <https://attack.mitre.org/techniques/T1014/>
