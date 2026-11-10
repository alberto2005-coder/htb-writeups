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
| CrownJewel-2 | DFIR / Active Directory | Medium | DC logs with pass-the-hash and `C$` access | EvtxECmd, Timeline Explorer | [Ver](crownjewel-2/README.en.md) |
| Campfire-2 | DFIR / Active Directory | Easy | 4768 without pre-authentication (AS-REP) and later use | EvtxECmd, 4768/4769 | [Ver](campfire-2/README.en.md) |
| Safecracker | DFIR / Malware | Medium | Ransomware with a custom extension and embedded key | Ghidra, `strings`, PE-bear | [Ver](safecracker/README.en.md) |
| JenkreadD | DFIR / Web | Easy | Jenkins CVE-2024-23897: `POST /cli` with `@path` | `grep`, log analysis | [Ver](jenkreadd/README.en.md) |
| Subatomic | Malware / DFIR | Medium | Electron app stealing the Discord token with persistence | `asar`, JS analysis | [Ver](subatomic/README.en.md) |
| Litter | SOC | Easy | PCAP + ZIP from a test host | Wireshark, dnscat2-decoder | [Ver](litter/README.en.md) |
| PhantomRing | Malware Analysis | Very Easy | Post-exploitation ELF binary | Ghidra, `strings`, `file` | [Ver](phantomring/README.md) |
| Opportunist | DFIR / Malware | Medium | Memory + triage from a corporate host | Volatility 3, VirusTotal, ChromeCacheView, SQLECmd | [Ver](opportunist/README.md) |
| dOOMs Day | DFIR | Medium | Web logs from a compromised PHP server | access-log analysis, PHP2Shell | [Ver](dooms-day/README.md) |
| Brutus | DFIR | Very Easy | Authentication logs | `grep`, `awk`, timeline | [Ver](brutus/README.md) |
| MangoBleed | DFIR | Very Easy | Windows triage | EvtxECmd, timeline | [Ver](mangobleed/README.md) |
| NeuroSync-D | DFIR | Easy | Artifacts from a medical-device vendor | RegRipper, MFT | [Ver](neurosync-d/README.md) |
| Campfire-1 | DFIR / Active Directory | Very Easy | Domain event logs | EvtxECmd, 4769 analysis | [Ver](campfire-1/README.md) |
| CrownJewel-1 | DFIR / Active Directory | Medium | DC telemetry after a compromise | 4662/4769 events, correlation | [Ver](crownjewel-1/README.md) |
| Loggy | DFIR | Very Easy | Web server logs | `awk`, `grep`, timeline | [Ver](loggy/README.md) |
| Bumblebee | DFIR | Easy | phpBB SQLite database and `access.log` | `sqlite3`, `grep`, IP correlation | [Ver](bumblebee/README.en.md) |
| Meerkat | SOC | Easy | PCAP and Suricata alerts | Wireshark, `tshark`, `jq` | [Ver](meerkat/README.en.md) |
| Tracer | DFIR | Easy | PSEXESVC logs and `Prefetch` | PECmd, MFTECmd, Timeline Explorer | [Ver](tracer/README.en.md) |
| Noted | DFIR | Easy | Notepad++ artefacts | `config.xml`, backups, OSINT | [Ver](noted/README.en.md) |
| Logjammer | Log Analysis | Easy | Five EVTX channels from one host | EvtxECmd, Timeline Explorer | [Ver](logjammer/README.en.md) |
| Unit42 | DFIR | Very Easy | Sysmon y Dropbox en un host Windows | Sysmon, EvtxECmd, timestomping | [Ver](unit42/README.en.md) |
| BFT | DFIR | Very Easy | `$MFT` de un ZIP troyanizado | MFTECmd, `grep`, offsets | [Ver](bft/README.en.md) |
| Noxious | DFIR | Medium | PCAP con envenenamiento LLMNR/NBT-NS | Wireshark, hashcat `-m 5600` | [Ver](noxious/README.en.md) |
| Reaper | DFIR | Very Easy | `ntlmrelay.pcapng` y `Security.evtx` | Wireshark, EvtxECmd | [Ver](reaper/README.en.md) |
| Knock Knock | DFIR | Easy | PCAP de *password spray* y *port knocking* | Wireshark, `tshark` | [Ver](knock-knock/README.en.md) |
| RogueOne | DFIR / Memoria | Medium | Volcado de memoria de un puesto Forela | Volatility 3, `windows.netscan` | [Ver](rogueone/README.en.md) |
| SSHole | DFIR / Unix | Very Easy | Evidencias de un jumpbox comprometido | `auth.log`, `last`, `journalctl` | [Ver](sshole/README.en.md) |
| ShadowBait | DFIR / Windows | Easy | Logs de Sysmon, PowerShell y Security | Hayabusa, EvtxECmd | [Ver](shadowbait/README.en.md) |
| Compromised | DFIR / Red | Easy | PCAP de una red corporativa | Wireshark, `tshark` | [Ver](compromised/README.en.md) |
| Packet Puzzle | DFIR / Red | Medium | PCAP de una empresa de criptomonedas | Wireshark, `tshark` | [Ver](packet-puzzle/README.en.md) |
| Jingle Bell | DFIR / Windows | Easy | Base de notificaciones de Windows de un puesto | SQLite, DB Browser | [Ver](jingle-bell/README.en.md) |
| Ultimatum | DFIR / Web | Easy | Logs y ficheros de un WordPress comprometido | `access.log`, WP-CLI | [Ver](ultimatum/README.en.md) |
| ProcNet | DFIR / Endpoint | Hard | PCAP, API Monitor y Sysmon de DC y puesto | API Monitor, EvtxECmd | [Ver](procnet/README.en.md) |
| PCAP Analysis | DFIR / Red | Very Easy | Una captura de tráfico de un usuario | Wireshark, `tshark` | [Ver](pcap-analysis/README.en.md) |
| Vantage | DFIR / Red | Very Easy | PCAP de servidor web y controlador de nube | Wireshark, `tshark` | [Ver](vantage/README.en.md) |
| Lockpick | Malware / Ransomware | Easy | Muestra de ransomware y ficheros cifrados | Ghidra, x64dbg | [Ver](lockpick/README.en.md) |
| Lockpick 2.0 | Malware / Ransomware | Easy | Recurso compartido cifrado y muestra con nota | UPX, Ghidra | [Ver](lockpick-2/README.en.md) |
| Payload | Malware / Windows | Easy | Ejecutable MinGW con payload cifrado en runtime | x64dbg, PE-bear | [Ver](payload/README.en.md) |
| Takedown | Red / DFIR | Easy | PCAP con SMB, VBS y PowerShell hacia un C2 | Wireshark, `tshark` | [Ver](takedown/README.en.md) |
| Interceptor | SOC / Red | Easy | PCAP de una infección SSLoad con C2 en RC4 | Wireshark, CyberChef | [Ver](interceptor/README.en.md) |
| Nubilum-1 | Cloud / AWS | Medium | CloudTrail, EC2 comprometida y copia de S3 | `jq`, AWS CLI | [Ver](nubilum-1/README.en.md) |
| Nubilum-2 | Cloud / AWS | Medium | Bucket S3 con política pública y claves creadas | Splunk, `jq` | [Ver](nubilum-2/README.en.md) |
| Hyperfiletable | DFIR / Windows | Easy | Sólo la MFT de un equipo con phishing | MFTECmd, MFTExplorer | [Ver](hyperfiletable/README.en.md) |
| WorkFromHome | DFIR / Windows | Medium | Robo de credenciales, RDP y secuestro de DLL en WMI | SRUM, MFT, KAPE | [Ver](workfromhome/README.en.md) |
| Lockpick 3.0 | Malware / Linux | Medium | Binario con XOR, volcado de memoria y unidad systemd | Volatility 3, Ghidra | [Ver](lockpick-3/README.en.md) |

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
