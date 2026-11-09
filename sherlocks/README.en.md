# Sherlocks — Hack The Box

**English** | [🇪🇸 Español](README.md)

**Sherlocks** are defensive investigation scenarios: nothing is attacked, you answer questions about an incident from evidence (memory images, disk dumps, logs, PCAP, binaries). This directory holds the notes for the ones I document, with scenario, tooling and reasoning; platform answers are not published verbatim.

## How it works

1. Download a ZIP with the evidence (usual password: `hacktheblue`).
2. Inside there is a `README` with the scenario and the questions.
3. Answers go into the platform; each correct one scores.

Artifacts may contain real malware: work in an isolated VM with no network.

## Notes

| Sherlock | Domain | Difficulty | Main evidence | Tools | Note |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP + ZIP from a test host | Wireshark, dnscat2-decoder | [Ver](litter/README.en.md) |
| PhantomRing | Malware Analysis | Very Easy | Post-exploitation ELF binary | Ghidra, `strings`, `file` | pending |
| Opportunist | DFIR / Malware | Medium | Memory + triage from a corporate host | Volatility 3, VirusTotal, ChromeCacheView, SQLECmd | pending |
| dOOMs Day | DFIR | Medium | Web logs from a compromised PHP server | access-log analysis, PHP2Shell | pending |
| Brutus | DFIR | Very Easy | Authentication logs | `grep`, `awk`, timeline | pending |
| MangoBleed | DFIR | Very Easy | Windows triage | EvtxECmd, timeline | pending |
| NeuroSync-D | DFIR | Easy | Artifacts from a medical-device vendor | RegRipper, MFT | pending |

## Shared methodology

1. **Inventory**: list files, sizes and hashes before opening anything. Note what is original and what you generated.
2. **Context**: read the scenario twice and write down what you are looking for (who, when, how, what left the building).
3. **Triage**: start with whatever gives a quick timeline (execution, logons, connections), not with detail.
4. **Correlation**: back every conclusion with two sources; one is not evidence.
5. **Write-up**: format it as "question → evidence → reasoning", with paths and hashes.

## Conventions

- One folder per Sherlock with `README.md` and `README.en.md`.
- Platform answers are never copied; the method and evidence are what gets documented.
- Template: `templates/sherlock-template.md` and `.en.md`.
- The **Rameh** Sherlock is not yet identified in the HTB catalogue; it stays pending until the name and domain are confirmed.
