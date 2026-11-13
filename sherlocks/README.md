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
| Phantom Check | DFIR | Very Easy | Dos EVTX de PowerShell: WMI y anti-VM | EvtxECmd, KAPE | [Ver](phantom-check/README.md) |
| TickTock | DFIR / Windows | Medium | MFT, TeamViewer, PowerShell y Defender | MFTECmd, Chainsaw, EvtxECmd | [Ver](ticktock/README.md) |
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
| Heartbreaker-Denouement | Cloud / AWS | Medium | SSRF al servicio de metadatos, credenciales de rol y snapshots de RDS compartidos | CloudTrail en JSONL, `grep`, `jq` | [Ver](heartbreaker-denouement/README.md) |
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
| Jugglin | DFIR / WSL2 | Medium | Capturas de API de `wsl.exe`: exfiltración y volcado con `lsassy` sin rastro en logs de Windows | API Monitor | [Ver](jugglin/README.md) |
| Heist | DFIR / Malware | Hard | Phishing → `Partnership.pdf.exe` → RedLine; PCAP, Prefetch y SRUM | Wireshark, SrumECmd | [Ver](heist/README.md) |
| BOughT | DFIR / Malware | Hard | Memoria + AD1: persistencia en `StartUp`, mutex, DGA de 59.049 dominios y DDoS | Volatility 2, Ghidra | [Ver](bought/README.md) |
| Liberty | DFIR / Windows | Medium | Spray → RDP, robo de Net-NTLMv2 con un `.url` y PowerShell Web Access | EvtxECmd, MFTECmd | [Ver](liberty/README.md) |
| Jinkies | DFIR / Windows | Medium | SMB con credenciales, backup `bk_db.ibd` y reutilización hasta el hash local | Chainsaw, MFTECmd | [Ver](jinkies/README.md) |
| i-like-to | DFIR / MOVEit | Easy | Triaje KAPE de un servidor MOVEit: IIS logs, `$MFT`, EVTX, memoria y volcado SQL | MFTECmd, EvtxECmd, `strings` | [Ver](i-like-to/README.md) |
| Pikaptcha | DFIR / Windows | Easy | PCAP y KAPE: captcha falso, portapapeles y PowerShell | Wireshark, regipy | [Ver](pikaptcha/README.md) |
| Constellation | Threat Intelligence | Medium | PDF con instrucciones a un insider: metadatos y URLs con hora | exiftool, Unfurl | [Ver](constellation/README.md) |
| Heartbreaker-Continuum | DFIR / Malware | Easy | `.tiff.exe` con PowerShell compilado y exfiltración SFTP | PEStudio, CyberChef, Ghidra | [Ver](heartbreaker-continuum/README.md) |
| MisCloud | Cloud / GCP | Medium | Hook `post-receive`, cuenta de servicio y exfiltración desde un bucket | Wireshark, `jq` | [Ver](miscloud/README.md) |
| Hunter | Threat Hunting | Insane | Triaje de endpoint y PCAP parcial: servicio 7045, Amcache, Prefetch, `Windows.edb` y FileZilla | EvtxECmd, PECmd, SIDR, Wireshark | [Ver](hunter/README.md) |
| Trent | DFIR / Red | Medium | PCAP de un router: CVE-2024-28353 y reverse shell | Wireshark, `tshark` | [Ver](trent/README.md) |
| Einladen | DFIR / Windows | Medium | HTML smuggling → HTA → DLL side-loading y C2 | Procmon, Wireshark, CyberChef | [Ver](einladen/README.md) |
| Recollection | DFIR / Memoria | Easy | Volcado de memoria con PowerShell ofuscado e inyección | Volatility 3 | [Ver](recollection/README.md) |
| Mellitus | DFIR / Memoria | Medium | Memoria, historial de Chrome, hashes locales e imagen invertida | Volatility 3, `sqlite3`, Pillow | [Ver](mellitus/README.md) |
| Nuts | DFIR / Windows | Medium | Typosquat de NuGet, `init.ps1`, persistencia y Defender | NuGet, PECmd, EvtxECmd | [Ver](nuts/README.md) |
| Ore | DFIR / Linux | Medium | Grafana CVE-2021-43798, credenciales y minero `xmrig` | `sqlite3`, `ps`, `ss` | [Ver](ore/README.md) |
| Conned-Again | DFIR / Linux | Easy | Triaje CatScale de Confluence: CVE-2023-22515 y CVE-2023-22527 | `grep`, análisis de logs | [Ver](conned-again/README.md) |
| Kuber | DFIR / Kubernetes | Easy | NodePort SSH, secretos en base64 y pod falso en `kube-system` | `grep`, YAML, `base64` | [Ver](kuber/README.md) |
| Exitiabilis | SOC / Windows | Medium | HELK y VPN AnyConnect: correlación de logon, ejecución y persistencia | Kibana, EvtxECmd | [Ver](exitiabilis/README.md) |
| DroidPhish | DFIR / Android | Easy | Imagen ext4, Proton Mail, APK sideloaded y C2 en base64 | `debugfs`, `sqlite3`, Androguard | [Ver](droidphish/README.md) |
| Unsupervised | DFIR / Windows | Medium | USB, `USBSTOR`, jump lists y thumbcache en una exfiltración | Registry Explorer, JLECmd | [Ver](unsupervised/README.md) |
| Heartbreaker | DFIR / Windows | Medium | Triaje KAPE, OST de Outlook, MFT y WinSCP | libpff, MFTECmd, Timeline Explorer | [Ver](heartbreaker/README.md) |
| APTNightmare | DFIR / Red y memoria | Medium | PCAP, reverse shell, memoria y beacon de Cobalt Strike | Wireshark, strings, 1768.py | [Ver](aptnightmare/README.md) |
| Detroit becomes Human | DFIR / Windows | Hard | MSI falso, script de PowerShell y extensión de Chrome | MFTECmd, Chainsaw, Timeline Explorer | [Ver](detroit-becomes-human/README.md) |
| OpTinselTrace-1 | DFIR / Insider | Easy | eM Client, correo enviado, ZIP y MFT/USN | eM Client, JLECmd, MFTECmd | [Ver](optinseltrace-1/README.md) |
| OpTinselTrace-2 | DFIR / AWS | Easy | CloudTrail, claves IAM y acceso a S3 | `jq`, AWS CLI | [Ver](optinseltrace-2/README.md) |
| OpTinselTrace-3 | DFIR / Memoria | Medium | Memoria Windows, LNK, PowerShell ofuscado y Defender | Volatility 3, CyberChef, IDA | [Ver](optinseltrace-3/README.md) |
| OpTinselTrace-4 | DFIR / Red | Easy | PCAP de impresión, PJL y SSH; ZIP con AES | 7-Zip, Wireshark, `tshark` | [Ver](optinseltrace-4/README.md) |
| OpTinselTrace-5 | DFIR / Windows | Hard | EVTX, servicios 7045, propagación y ransomware | Chainsaw, Sigma | [Ver](optinseltrace-5/README.md) |
| SmartyPants | DFIR / Windows | Very Easy | EVTX de RDP (1149), SmartScreen y borrado de logs (1102) | EvtxECmd, Timeline Explorer | [Ver](smartypants/README.md) |
| Allegretto | DFIR / Windows | Medium | Imagen EWF con BitLocker, Thunderbird y papelera | ewfmount, dissect, RECmd | [Ver](allegretto/README.md) |
| Salsa Dance | DFIR / Windows | Medium | EVTX, MFT, PowerShell y línea temporal | EvtxECmd, MFTECmd, Chainsaw | [Ver](salsa-dance/README.md) |
| Cinder | DFIR / Windows | Easy | Persistencia en registro/servicios y ejecución | Registry Explorer, PECmd | [Ver](cinder/README.md) |
| Fleet | DFIR / Windows | Easy | Correlación multi-host y movimiento lateral | EvtxECmd, Timeline Explorer | [Ver](fleet/README.md) |
| Grabber | Malware Analysis | Medium | Infostealer, navegadores/wallets y C2 | PEStudio, Procmon, Wireshark | [Ver](grabber/README.md) |
| Hat Trick | DFIR / Windows | Easy | Tareas programadas y acceso a credenciales | EvtxECmd, Autoruns | [Ver](hat-trick/README.md) |
| Infiltrate | DFIR / Red | Easy | PCAP, SMB/WinRM y correlación con EVTX | Wireshark, Zeek, EvtxECmd | [Ver](infiltrate/README.md) |
| Backdoor | DFIR / Windows | Easy | IIS, webshell y persistencia | EvtxECmd, MFTECmd, PECmd | [Ver](backdoor/README.md) |
| BlackEnergy | Malware Analysis | Medium | Dropper, persistencia y C2 | DIE, CAPA, Procmon | [Ver](blackenergy/README.md) |
| Mysterious | DFIR / Windows | Easy | USB, LNK y tareas programadas | Registry Explorer, JLECmd | [Ver](mysterious/README.md) |
| Lit | DFIR / Windows | Easy | Fuerza bruta RDP y eventos 4625/4624 | EvtxECmd, Timeline Explorer | [Ver](lit/README.md) |
| Alchemy | DFIR / Windows | Medium | PowerShell ofuscado y acceso a credenciales | EvtxECmd, Volatility | [Ver](alchemy/README.md) |
| Artifact | DFIR / Windows | Easy | MFT, archivos comprimidos y exfiltración | MFTECmd, PECmd | [Ver](artifact/README.md) |
| Oxide | DFIR / Windows | Medium | Memoria, inyección de procesos y C2 | Volatility, MemProcFS | [Ver](oxide/README.md) |
| Pwned | DFIR / Windows | Easy | Ransomware y borrado de copias de sombra | EvtxECmd, MFTECmd | [Ver](pwned/README.md) |
| Fragility | DFIR | Easy | Archivo exfiltrado, metadatos y codificación | 7-Zip, ExifTool, CyberChef | [Ver](fragility/README.md) |
| LATUS | DFIR / Windows | Medium | EVTX, MFT, registro y línea temporal | EvtxECmd, MFTECmd | [Ver](latus/README.md) |
| TrainingDay | Malware Analysis | Easy | Macro, dropper y persistencia | oletools, Procmon | [Ver](trainingday/README.md) |
| SecretPictures | Malware Analysis | Easy | Gusano Go, USB, Run y C2 | DIE, Registry Explorer | [Ver](secretpictures/README.md) |
| Kawmikaze | Malware Analysis | Medium | Loader, inyección y C2 | CAPA, Volatility | [Ver](kawmikaze/README.md) |
| SalineBreeze-2 | DFIR | Easy | Logs, PCAP y movimiento lateral | Zeek, Wireshark | [Ver](salinebreeze-2/README.md) |
| ElectricBreeze-2 | Malware Analysis | Easy | JAR, webshell y credenciales | jadx, YARA | [Ver](electricbreeze-2/README.md) |
| ShadowStream | Malware Analysis | Medium | Loader multicapa y persistencia | CAPA, Volatility | [Ver](shadowstream/README.md) |
| WhyFind | DFIR | Easy | Prefetch, Amcache y ejecución desde USB | KAPE, Timeline Explorer | [Ver](whyfind/README.md) |
| Cuidado | SOC | Easy | Tráfico HTTP, binario UPX y C2 | Wireshark, CyberChef | [Ver](cuidado/README.md) |
| PercyPay | Cloud | Easy | Función Lambda, credenciales y persistencia | AWS CLI, CloudTrail | [Ver](percypay/README.md) |
| ReliableThreat | DFIR | Medium | Extensión de VS Code y ejecución de PowerShell | KAPE, Registry Explorer | [Ver](reliablethreat/README.md) |
| GateKeeper | DFIR | Hard | Artefactos macOS, LaunchAgents y binario firmado | KnockKnock, Plaso | [Ver](gatekeeper/README.md) |
| PhishNet | SOC | Very Easy | Cabeceras, SPF, adjunto base64 y ZIP | Wireshark, CyberChef | [Ver](phishnet/README.md) |
| RomCom | DFIR | Very Easy | CVE-2025-8088, MFT, USN y USB | MFTECmd, PECmd | [Ver](romcom/README.md) |
| Whisper | DFIR | Easy | Registro, MFT, Mimikatz y ShellBags | Registry Explorer, MFTECmd | [Ver](whisper/README.md) |
| Zenith | DFIR | Easy | Correo, EVTX, persistencia y escalada | EvtxECmd, Timeline Explorer | [Ver](zenith/README.md) |
| Psittaciformes | DFIR | Easy | Logs, `.bash_history` y repositorio Git | Git, Plaso | [Ver](psittaciformes/README.md) |
| HookFlare | DFIR | Medium | Smishing Android, 2FA y AES-ECB | JADX, Wireshark | [Ver](hookflare/README.md) |
| CrewCrow | DFIR | Medium | Zoom, DPAPI y hashes NTLM | DPAPI, Hashcat | [Ver](crewcrow/README.md) |
| Caught | DFIR | Hard | JScript, Sliver, GPO y persistencia WMI | Sysmon, EvtxECmd | [Ver](caught/README.md) |

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
