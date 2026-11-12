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
| Phantom Check | DFIR | Very Easy | Two PowerShell EVTX logs: WMI and anti-VM | EvtxECmd, KAPE | [Ver](phantom-check/README.md) |
| TickTock | DFIR / Windows | Medium | MFT, TeamViewer, PowerShell and Defender | MFTECmd, Chainsaw, EvtxECmd | [Ver](ticktock/README.md) |
| CrownJewel-2 | DFIR / Active Directory | Medium | DC logs with pass-the-hash and `C$` access | EvtxECmd, Timeline Explorer | [Ver](crownjewel-2/README.en.md) |
| Campfire-2 | DFIR / Active Directory | Easy | 4768 without pre-authentication (AS-REP) and later use | EvtxECmd, 4768/4769 | [Ver](campfire-2/README.en.md) |
| Safecracker | DFIR / Malware | Medium | Ransomware in a ZIP for Autopsy: accounts, encryption and deletion via `NtSetInformationFile` | Ghidra, `strings`, PE-bear | [Ver](safecracker/README.en.md) |
| JenkreadD | DFIR / Web | Easy | Jenkins CVE-2024-23897: `POST /cli` with `@path` | `grep`, log analysis | [Ver](jenkreadd/README.en.md) |
| Subatomic | Malware / DFIR | Medium | Fake game installer: Electron `app.asar`, Discord token theft and `openAtLogin` | `asar`, JS analysis | [Ver](subatomic/README.en.md) |
| Litter | SOC | Easy | PCAP + ZIP from a test host | Wireshark, dnscat2-decoder | [Ver](litter/README.en.md) |
| PhantomRing | Malware Analysis | Very Easy | Unstripped ELF in `/var/tmp`: `nm` yields the names and the C2 port is an immediate operand | Ghidra, `strings`, `file` | [Ver](phantomring/README.md) |
| Opportunist | DFIR / Malware | Medium | Memory + triage from a corporate host | Volatility 3, VirusTotal, ChromeCacheView, SQLECmd | [Ver](opportunist/README.md) |
| dOOMs Day | DFIR | Easy | Web logs from a compromised PHP server | access-log analysis, PHP2Shell | [Ver](dooms-day/README.md) |
| Brutus | DFIR | Very Easy | Authentication logs | `grep`, `awk`, timeline | [Ver](brutus/README.md) |
| MangoBleed | DFIR / Linux | Very Easy | UAC MongoDB triage: CVE-2025-14847 and `/var/lib/mongodb` exfiltration | `mongod.log`, `auth.log`, `grep` | [Ver](mangobleed/README.en.md) |
| NeuroSync-D | DFIR / Web | Easy | Next.js CVE-2025-29927 → SSRF, LFI and Redis to RCE | `interface.log`, `data-api.log`, `grep` | [Ver](neurosync-d/README.en.md) |
| Campfire-1 | DFIR / Active Directory | Very Easy | Domain event logs | EvtxECmd, 4769 analysis | [Ver](campfire-1/README.md) |
| CrownJewel-1 | DFIR / Active Directory | Medium | DC telemetry after a compromise | 4662/4769 events, correlation | [Ver](crownjewel-1/README.md) |
| Loggy | Malware / Go | Easy | `Loggy.exe`: Go keylogger with screenshots and FTP exfiltration | Ghidra, `strings`, CyberChef | [Ver](loggy/README.en.md) |
| Bumblebee | DFIR | Easy | phpBB SQLite database and `access.log` | `sqlite3`, `grep`, IP correlation | [Ver](bumblebee/README.en.md) |
| Heartbreaker-Denouement | Cloud / AWS | Medium | SSRF to the metadata service, role credentials and shared RDS snapshots | CloudTrail as JSONL, `grep`, `jq` | [Ver](heartbreaker-denouement/README.en.md) |
| Meerkat | SOC | Easy | PCAP and Suricata alerts | Wireshark, `tshark`, `jq` | [Ver](meerkat/README.en.md) |
| Tracer | DFIR | Easy | PsExec nine times: `psexesvc.exe`, `.key`, named pipes and source host | PECmd, MFTECmd, Timeline Explorer | [Ver](tracer/README.en.md) |
| Noted | DFIR | Easy | Notepad++ artefacts | `config.xml`, backups, OSINT | [Ver](noted/README.en.md) |
| Logjammer | Log Analysis | Easy | Five EVTX channels from one host | EvtxECmd, Timeline Explorer | [Ver](logjammer/README.en.md) |
| Unit42 | DFIR | Very Easy | Sysmon y Dropbox en un host Windows | Sysmon, EvtxECmd, timestomping | [Ver](unit42/README.en.md) |
| BFT | DFIR | Very Easy | `$MFT` de un ZIP troyanizado | MFTECmd, `grep`, offsets | [Ver](bft/README.en.md) |
| Noxious | DFIR | Medium | PCAP with LLMNR/NBT-NS poisoning | Wireshark, hashcat `-m 5600` | [Ver](noxious/README.en.md) |
| Reaper | DFIR | Very Easy | NTLM relay after a mistyped share: LLMNR, a 4624 whose IP and workstation disagree, 5140 | Wireshark, EvtxECmd | [Ver](reaper/README.en.md) |
| Knock Knock | DFIR | Medium | PCAP de *password spray* y *port knocking* | Wireshark, `tshark` | [Ver](knock-knock/README.en.md) |
| RogueOne | DFIR / Memoria | Easy | Fake `svchost.exe` in `Downloads` with C2 to 13.127.155.166:8888 and a `cmd.exe` child | Volatility 3, `windows.netscan` | [Ver](rogueone/README.en.md) |
| SSHole | DFIR / Unix | Very Easy | Alpine `sshd` bypass (crypt's `*`) on a jumpbox later used to scan `192.168.18.0/24` | `auth.log`, `last`, `journalctl` | [Ver](sshole/README.en.md) |
| ShadowBait | DFIR / Windows | Easy | Steven's Office document → PowerShell → C2 `192.168.204.152:8899` → DPAPI and persistence | Hayabusa, EvtxECmd | [Ver](shadowbait/README.en.md) |
| Compromised | DFIR / Red | Easy | PCAP de una red corporativa | Wireshark, `tshark` | [Ver](compromised/README.en.md) |
| Packet Puzzle | DFIR / Red | Medium | PCAP from a Japanese crypto company: CVE-2024-4577 in PHP 8.1.25 over POST, `cristo`, `nc64.exe`, GodPotato and `Win32Error:2` (`[CORREGIDO]` per cyb3rloud and FinalBreach) | Wireshark, `tshark` | [Ver](packet-puzzle/README.en.md) |
| Jingle Bell | DFIR / Windows | Easy | Base de notificaciones de Windows de un puesto | SQLite, DB Browser | [Ver](jingle-bell/README.en.md) |
| Ultimatum | DFIR / Web | Easy | CVE-2023-3460 in Ultimate Member: `secragon` admin, web shell and remote shell | `access.log`, WP-CLI | [Ver](ultimatum/README.en.md) |
| ProcNet | DFIR / Endpoint | Hard | Open-source C2: JA3, API Monitor (Vault) and Sysmon from employee and DC | API Monitor, EvtxECmd | [Ver](procnet/README.en.md) |
| PCAP Analysis | DFIR / Red | Very Easy | P13's capture: cleartext chat on TCP/250 and a ~107 KB HTTP upload to another subnet | Wireshark, `tshark` | [Ver](pcap-analysis/README.en.md) |
| Vantage | DFIR / Red | Very Easy | PCAP de servidor web y controlador de nube | Wireshark, `tshark` | [Ver](vantage/README.en.md) |
| Lockpick | Malware / Ransomware | Easy | Muestra de ransomware y ficheros cifrados | Ghidra, x64dbg | [Ver](lockpick/README.en.md) |
| Lockpick 2.0 | Malware / Ransomware | Easy | Recurso compartido cifrado y muestra con nota | UPX, Ghidra | [Ver](lockpick-2/README.en.md) |
| Payload | Malware / Windows | Easy | `func_pointer.exe` (MinGW) decrypting its payload at runtime | x64dbg, radare2, PEStudio | [Ver](payload/README.en.md) |
| Takedown | Red / DFIR | Easy | PCAP with SMB2 → `.vbs` → PowerShell → C2, plus `NTLMSSP_AUTH` for pass-the-hash | Wireshark, `tshark` | [Ver](takedown/README.en.md) |
| Interceptor | SOC / Red | Easy | PCAP de una infección SSLoad con C2 en RC4 | Wireshark, CyberChef | [Ver](interceptor/README.en.md) |
| Nubilum-1 | Cloud / AWS | Medium | CloudTrail, EC2 comprometida y copia de S3 | `jq`, AWS CLI | [Ver](nubilum-1/README.en.md) |
| Nubilum-2 | Cloud / AWS | Medium (sources: Easy) | S3 with anonymous read of an IAM key CSV and self-escalation via `PutUserPolicy` | Splunk, `jq` | [Ver](nubilum-2/README.en.md) |
| Hyperfiletable | DFIR / Windows | Easy | Sólo la MFT de un equipo con phishing | MFTECmd, MFTExplorer | [Ver](hyperfiletable/README.en.md) |
| WorkFromHome | DFIR / Windows | Medium | Phishing → RDP → `SeManageVolumePrivilege` → `PrintConfig.dll` and WMI persistence | SRUM, MFT, KAPE | [Ver](workfromhome/README.en.md) |
| Lockpick 3.0 | Malware / Linux | Hard | XOR binary with the key passed as an argument, memory and systemd unit | Volatility 3, Ghidra | [Ver](lockpick-3/README.en.md) |
| Jugglin | DFIR / WSL2 | Medium | `wsl.exe` API captures: exfiltration and `lsassy` dumping with no Windows log trace | API Monitor | [Ver](jugglin/README.en.md) |
| Heist | DFIR / Malware | Hard | Phishing → `Partnership.pdf.exe` → RedLine; PCAP, Prefetch and SRUM | Wireshark, SrumECmd | [Ver](heist/README.en.md) |
| BOughT | DFIR / Malware | Hard | Memory + AD1: `StartUp` persistence, mutex, 59,049-domain DGA and DDoS | Volatility 2, Ghidra | [Ver](bought/README.en.md) |
| Liberty | DFIR / Windows | Medium | Spray → RDP, Net-NTLMv2 theft via a `.url` and PowerShell Web Access | EvtxECmd, MFTECmd | [Ver](liberty/README.en.md) |
| Jinkies | DFIR / Windows | Medium | SMB with credentials, `bk_db.ibd` backup and reuse down to the local hash | Chainsaw, MFTECmd | [Ver](jinkies/README.en.md) |
| i-like-to | DFIR / MOVEit | Easy | KAPE triage of a MOVEit server: IIS logs, `$MFT`, EVTX, memory and SQL dump | MFTECmd, EvtxECmd, `strings` | [Ver](i-like-to/README.en.md) |
| Pikaptcha | DFIR / Windows | Easy | PCAP and KAPE: fake captcha, clipboard and PowerShell | Wireshark, regipy | [Ver](pikaptcha/README.en.md) |
| Constellation | Threat Intelligence | Medium | PDF with insider instructions: metadata and timestamped URLs | exiftool, Unfurl | [Ver](constellation/README.en.md) |
| Heartbreaker-Continuum | DFIR / Malware | Easy | `.tiff.exe` with compiled PowerShell and SFTP exfiltration | PEStudio, CyberChef, Ghidra | [Ver](heartbreaker-continuum/README.en.md) |
| MisCloud | Cloud / GCP | Medium | `post-receive` hook, service account and bucket exfiltration | Wireshark, `jq` | [Ver](miscloud/README.en.md) |
| Hunter | Threat Hunting | Insane | Endpoint triage and partial PCAP: 7045 service, Amcache, Prefetch, `Windows.edb` and FileZilla | EvtxECmd, PECmd, SIDR, Wireshark | [Ver](hunter/README.en.md) |
| Trent | DFIR / Network | Medium | Router PCAP: CVE-2024-28353 and a reverse shell | Wireshark, `tshark` | [Ver](trent/README.en.md) |
| Einladen | DFIR / Windows | Medium | HTML smuggling → HTA → DLL side-loading and C2 | Procmon, Wireshark, CyberChef | [Ver](einladen/README.en.md) |
| Recollection | DFIR / Memory | Easy | Memory dump with obfuscated PowerShell and injection | Volatility 3 | [Ver](recollection/README.en.md) |
| Mellitus | DFIR / Memory | Medium | Memory, Chrome history, local hashes and an inverted image | Volatility 3, `sqlite3`, Pillow | [Ver](mellitus/README.en.md) |
| Nuts | DFIR / Windows | Medium | NuGet typosquat, `init.ps1`, persistence and Defender | NuGet, PECmd, EvtxECmd | [Ver](nuts/README.en.md) |
| Ore | DFIR / Linux | Medium | Grafana CVE-2021-43798, credentials and the `xmrig` miner | `sqlite3`, `ps`, `ss` | [Ver](ore/README.en.md) |

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
