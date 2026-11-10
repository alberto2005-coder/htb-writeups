# Sherlocks — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Los **Sherlocks** son escenarios de investigación defensiva: no se ataca nada, se responde a preguntas sobre un incidente a partir de evidencias (imágenes de memoria, volcados de disco, logs, PCAP, binarios). Este directorio recoge las fichas de los que voy documentando, con el escenario, las herramientas y el razonamiento; no se publican respuestas literales de la plataforma.

## Cómo funciona

1. Se descarga un ZIP con las evidencias (contraseña habitual: `hacktheblue`).
2. Dentro hay un `README` con el escenario y las preguntas.
3. Se responde en la plataforma; cada respuesta correcta da puntos.

Los artefactos pueden contener malware real: se trabaja en una VM aislada y sin red.

## Fichas

| Sherlock | Dominio | Dificultad | Evidencia principal | Herramientas | Ficha |
|---|---|---|---|---|---|
| CrownJewel-2 | DFIR / Active Directory | Medium | Logs de DC con pass-the-hash y acceso a `C$` | EvtxECmd, Timeline Explorer | [Ver](crownjewel-2/README.md) |
| Campfire-2 | DFIR / Active Directory | Easy | 4768 sin preautenticación (AS-REP) y uso posterior | EvtxECmd, 4768/4769 | [Ver](campfire-2/README.md) |
| Safecracker | DFIR / Malware | Medium | Ransomware en un ZIP para Autopsy: cuentas, cifrado y borrado con `NtSetInformationFile` | Ghidra, `strings`, PE-bear | [Ver](safecracker/README.md) |
| JenkreadD | DFIR / Web | Easy | Jenkins CVE-2024-23897: `POST /cli` con `@ruta` | `grep`, análisis de logs | [Ver](jenkreadd/README.md) |
| Subatomic | Malware / DFIR | Medium | Instalador falso de juego: `app.asar` de Electron, robo del token de Discord y `openAtLogin` | `asar`, análisis JS | [Ver](subatomic/README.md) |
| Litter | SOC | Easy | PCAP + ZIP de un host de pruebas | Wireshark, dnscat2-decoder | [Ver](litter/README.md) |
| PhantomRing | Malware Analysis | Very Easy | ELF sin `strip` en `/var/tmp`: `nm` da los nombres y el puerto de C2 es un inmediato | Ghidra, `strings`, `file` | [Ver](phantomring/README.md) |
| Opportunist | DFIR / Malware | Medium | Memoria + triaje de un equipo corporativo | Volatility 3, VirusTotal, ChromeCacheView, SQLECmd | [Ver](opportunist/README.md) |
| dOOMs Day | DFIR | Easy | Logs web de un servidor PHP comprometido | análisis de access logs, PHP2Shell | [Ver](dooms-day/README.md) |
| Brutus | DFIR | Very Easy | Logs de autenticación | `grep`, `awk`, timeline | [Ver](brutus/README.md) |
| MangoBleed | DFIR / Linux | Very Easy | Triage UAC de MongoDB: CVE-2025-14847 y exfiltración de `/var/lib/mongodb` | `mongod.log`, `auth.log`, `grep` | [Ver](mangobleed/README.md) |
| NeuroSync-D | DFIR / Web | Easy | Next.js CVE-2025-29927 → SSRF, LFI y Redis hasta RCE | `interface.log`, `data-api.log`, `grep` | [Ver](neurosync-d/README.md) |
| Campfire-1 | DFIR / Active Directory | Very Easy | Logs de eventos de un dominio | EvtxECmd, análisis de 4769 | [Ver](campfire-1/README.md) |
| CrownJewel-1 | DFIR / Active Directory | Medium | Telemetría de DC tras un compromiso | Eventos 4662/4769, correlación | [Ver](crownjewel-1/README.md) |
| Loggy | Malware / Go | Easy | `Loggy.exe`: keylogger en Go con capturas y exfiltración por FTP | Ghidra, `strings`, CyberChef | [Ver](loggy/README.md) |
| Bumblebee | DFIR | Easy | Base SQLite de phpBB y `access.log` | `sqlite3`, `grep`, correlación de IPs | [Ver](bumblebee/README.md) |
| Meerkat | SOC | Easy | PCAP y alertas de Suricata | Wireshark, `tshark`, `jq` | [Ver](meerkat/README.md) |
| Tracer | DFIR | Easy | PsExec nueve veces: `psexesvc.exe`, `.key`, named pipes y host de origen | PECmd, MFTECmd, Timeline Explorer | [Ver](tracer/README.md) |
| Noted | DFIR | Easy | Artefactos de Notepad++ | `config.xml`, copias de seguridad, OSINT | [Ver](noted/README.md) |
| Logjammer | Log Analysis | Easy | Cinco canales EVTX de un host | EvtxECmd, Timeline Explorer | [Ver](logjammer/README.md) |
| Unit42 | DFIR | Very Easy | Sysmon y Dropbox en un host Windows | Sysmon, EvtxECmd, timestomping | [Ver](unit42/README.md) |
| BFT | DFIR | Very Easy | `$MFT` de un ZIP troyanizado | MFTECmd, `grep`, offsets | [Ver](bft/README.md) |
| Noxious | DFIR | Medium | PCAP con envenenamiento LLMNR/NBT-NS | Wireshark, hashcat `-m 5600` | [Ver](noxious/README.md) |
| Reaper | DFIR | Very Easy | NTLM relay tras un nombre mal escrito: LLMNR, 4624 con IP y equipo que no cuadran, 5140 | Wireshark, EvtxECmd | [Ver](reaper/README.md) |
| Knock Knock | DFIR | Medium | PCAP de *password spray* y *port knocking* | Wireshark, `tshark` | [Ver](knock-knock/README.md) |
| RogueOne | DFIR / Memoria | Easy | `svchost.exe` falso en `Downloads` con C2 a 13.127.155.166:8888 y `cmd.exe` hijo | Volatility 3, `windows.netscan` | [Ver](rogueone/README.md) |
| SSHole | DFIR / Unix | Very Easy | Bypass de `sshd` en Alpine (`*` de `crypt()`) en un jumpbox usado para escanear `192.168.18.0/24` | `auth.log`, `last`, `journalctl` | [Ver](sshole/README.md) |
| ShadowBait | DFIR / Windows | Easy | Documento de Office de Steven → PowerShell → C2 `192.168.204.152:8899` → DPAPI y persistencia | Hayabusa, EvtxECmd | [Ver](shadowbait/README.md) |
| Compromised | DFIR / Red | Easy | PCAP de una red corporativa | Wireshark, `tshark` | [Ver](compromised/README.md) |
| Packet Puzzle | DFIR / Red | Medium | PCAP de una empresa japonesa de criptomonedas: CVE-2024-4577 en PHP 8.1.25 vía POST, `cristo`, `nc64.exe`, GodPotato y `Win32Error:2` (`[CORREGIDO]` con cyb3rloud y FinalBreach) | Wireshark, `tshark` | [Ver](packet-puzzle/README.md) |
| Jingle Bell | DFIR / Windows | Easy | Base de notificaciones de Windows de un puesto | SQLite, DB Browser | [Ver](jingle-bell/README.md) |
| Ultimatum | DFIR / Web | Easy | CVE-2023-3460 en Ultimate Member: admin `secragon`, web shell y shell remota | `access.log`, WP-CLI | [Ver](ultimatum/README.md) |
| ProcNet | DFIR / Endpoint | Hard | C2 de código abierto: JA3, API Monitor (Vault) y Sysmon de empleado y DC | API Monitor, EvtxECmd | [Ver](procnet/README.md) |
| PCAP Analysis | DFIR / Red | Very Easy | Captura de P13: chat en claro en TCP/250 y subida HTTP de ~107 KB a otra subred | Wireshark, `tshark` | [Ver](pcap-analysis/README.md) |
| Vantage | DFIR / Red | Very Easy | PCAP de servidor web y controlador de nube | Wireshark, `tshark` | [Ver](vantage/README.md) |
| Lockpick | Malware / Ransomware | Easy | Muestra de ransomware y ficheros cifrados | Ghidra, x64dbg | [Ver](lockpick/README.md) |
| Lockpick 2.0 | Malware / Ransomware | Easy | Recurso compartido cifrado y muestra con nota | UPX, Ghidra | [Ver](lockpick-2/README.md) |
| Payload | Malware / Windows | Easy | `func_pointer.exe` (MinGW) que descifra el payload en runtime | x64dbg, radare2, PEStudio | [Ver](payload/README.md) |
| Takedown | Red / DFIR | Easy | PCAP con SMB2 → `.vbs` → PowerShell → C2, más `NTLMSSP_AUTH` para pass-the-hash | Wireshark, `tshark` | [Ver](takedown/README.md) |
| Interceptor | SOC / Red | Easy | PCAP de una infección SSLoad con C2 en RC4 | Wireshark, CyberChef | [Ver](interceptor/README.md) |
| Nubilum-1 | Cloud / AWS | Medium | CloudTrail, EC2 comprometida y copia de S3 | `jq`, AWS CLI | [Ver](nubilum-1/README.md) |
| Nubilum-2 | Cloud / AWS | Medium (fuentes: Easy) | S3 con lectura anónima de un CSV de claves IAM y autoescalada con `PutUserPolicy` | Splunk, `jq` | [Ver](nubilum-2/README.md) |
| Hyperfiletable | DFIR / Windows | Easy | Sólo la MFT de un equipo con phishing | MFTECmd, MFTExplorer | [Ver](hyperfiletable/README.md) |
| WorkFromHome | DFIR / Windows | Medium | Phishing → RDP → `SeManageVolumePrivilege` → `PrintConfig.dll` y persistencia WMI | SRUM, MFT, KAPE | [Ver](workfromhome/README.md) |
| Lockpick 3.0 | Malware / Linux | Hard | Binario con XOR y clave por argumento, memoria y unidad systemd | Volatility 3, Ghidra | [Ver](lockpick-3/README.md) |

## Metodología común

1. **Inventario**: listar ficheros, tamaños y hashes antes de abrir nada. Anotar qué es original y qué se ha generado.
2. **Contexto**: leer el escenario dos veces y escribir qué se busca (quién, cuándo, cómo, qué se llevó).
3. **Triaje**: empezar por lo que da línea temporal rápida (ejecución, logins, conexiones) y no por el detalle.
4. **Correlación**: cruzar dos fuentes para cada conclusión; una sola no vale como evidencia.
5. **Respuesta**: redactar en formato "pregunta → evidencia → razonamiento", con rutas y hashes.

## Convenciones

- Una carpeta por Sherlock con `README.md` y `README.en.md`.
- Nunca se copian respuestas de la plataforma; se documenta el método y la evidencia.
- Plantilla: `templates/sherlock-template.md` y `.en.md`.
