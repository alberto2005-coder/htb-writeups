---
sherlock: RogueOne
domain: DFIR / Memory
difficulty: Medium
platform: Hack The Box
evidence: Memory dump from a Forela workstation
tools: [Volatility 3, windows.netscan, windows.cmdline, strings]
---

# RogueOne — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The SIEM fires several alerts within a minute pointing at possible **C2** from Simon Stark's workstation (Forela). No suspicious processes are visible, so the SOC isolates the host and hands over a memory dump to confirm the channel and rebuild the timeline.

## Evidence

- A single file: a Windows memory dump (`20230810.mem`).

## Method

1. **Dump profile** and process list: look for orphans, legitimate-looking names on odd paths and anomalous parent-child links.

```bash
vol -f 20230810.mem windows.pslist
vol -f 20230810.mem windows.pstree
```

2. **Network connections** — the plugin that cracks it:

```bash
vol -f 20230810.mem windows.netscan | grep <PID>
```

It returns a connection from the suspect PID to an external IP on a high port (on this box, `13.127.155.166:8888`).

3. **Command line** of that process to see how and from where it started:

```bash
vol -f 20230810.mem windows.cmdline --pid <PID>
```

4. **Execution time**: `windows.netscan` plus process creation time (`pslist` with `--physical`) pins down when the channel was established.

5. **Binary fingerprint**: if the image can be dumped, `strings` and an MD5 hash identify it and make it searchable against intelligence.

## What it teaches

- A memory dump proves C2 even when the EDR sees nothing odd: `netscan` is the primary evidence.
- Parent-child relationships and the binary path expose the dropper.
- The timeline comes from combining process creation with the first packet of the channel.

## Pitfalls

- **Profiles**: Volatility 3 needs none, but some plugins fail on truncated dumps.
- **Ephemeral ports**: filtering by PID instead of port avoids update and telemetry noise.
- **Legit-looking names**: here the name gives nothing away; the anomaly is the path and the outbound connection.
