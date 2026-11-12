---
title: "Threat hunting: hipótesis, pivotes y evidencia"
tags: [threat-hunting, dfir, evtx, sysmon, pcap, mitre]
---

# Threat hunting: hipótesis, pivotes y evidencia

[🇬🇧 English](threat-hunting.en.md) | **Español**

## 1. Cuándo mirar aquí

Una alerta de baja confianza, un SOC recién desplegado o un incidente con captura incompleta. La caza no empieza por una herramienta, sino por una **hipótesis** verificable: «un servicio creado en una ruta de usuario implica ejecución con SYSTEM», «un proceso de Office que lanza `certutil` implica descarga». Sin hipótesis solo hay búsqueda de IOCs, y los IOCs caducan.

## 2. El ciclo

1. **Hipótesis**: qué técnica sospechas y qué artefacto la probaría.
2. **Fuentes**: qué datos tienes y cuáles faltan (EVTX, Sysmon, Prefetch, Amcache, MFT, PCAP, EDR).
3. **Consulta**: una búsqueda concreta, con ventana temporal y ámbito.
4. **Triaje**: separar lo anómalo de lo normal con línea base.
5. **Pivote**: de un hallazgo a otro artefacto que lo confirme o lo descarte.
6. **Conclusión**: técnica, evidencia, impacto y detecciones derivadas.

## 3. Fuentes que resuelven más

| Artefacto | Qué responde | Herramienta |
|---|---|---|
| `System.evtx` (7045) | servicios creados y binario asociado | EvtxECmd, Event Viewer |
| `Security.evtx` (4624/4625/4688) | logons, tipo de logon, procesos | EvtxECmd, Hayabusa |
| Prefetch | ejecución y primera/última vez | PECmd |
| Amcache | SHA1 de ejecutables y rutas | AmcacheParser |
| `Windows.edb` | contenido indexado de documentos | SIDR (Search Index DB Reporter) |
| `CryptnetUrlCache` | URLs y contenido descargado por `certutil` | revisión directa |
| `PSReadLine` | comandos escritos en PowerShell | `ConsoleHost_history.txt` |
| `NTUser.dat` → UserAssist | programas usados y tiempo de foco | Registry Explorer |
| `UsrClass.dat` → shellbags | carpetas visitadas | ShellBags Explorer |
| PCAP | C2, exfiltración, credenciales en claro | Wireshark, `tshark` |

En Windows 11 el índice pasa a SQLite (`Windows.db`); SIDR parsea ambos formatos (ESE y SQLite).

## 4. Órdenes útiles

```bash
EvtxECmd.exe -f System.evtx --csv . --csvf system
PECmd.exe -d Prefetch --csv . --csvf prefetch
AmcacheParser.exe -f Amcache.hve --csv . --csvf amcache
tshark -r capture.pcap -Y "ftp || ftp-data" -T fields -e ip.src -e ip.dst -e ftp.request.command
```

Para correlacionar, normalizar todo a UTC y ordenar por hora. Un `4624` tipo 3 seguido de `whoami` y `certutil` cuenta una historia; cada evento por separado, no.

## 5. Pivotes típicos

- Servicio con nombre aleatorio → hash en Amcache →VT y prefetch del binario.
- `certutil` en Prefetch → `CryptnetUrlCache\MetaData` (URL) y `\Content` (fichero).
- Navegador → historial de descargas → herramientas de exfiltración y volcado.
- `PSReadLine` → script renombrado → cmdlets que delatan la familia.
- Shellbags → carpeta sensible → ZIP → PCAP → transferencia FTP.
- Volcado de proceso → CVE del producto → credenciales → base de datos.

## 6. Mapear a ATT&CK sin inventar

Se mapea lo **probado**, no lo supuesto. Un 7045 con binario en `Users\` es T1569.002 (Service Execution); un `certutil -urlcache` es T1105 (Ingress Tool Transfer); un `4624` tipo 10 es T1021.001 (RDP). Si la evidencia no alcanza, se escribe «no confirmado» y se propone la fuente que lo resolvería.

## 7. Documentar

- Línea temporal con hora y zona.
- Tabla hallazgo → artefacto → ruta → interpretación.
- IOCs separados de TTPs.
- Detecciones propuestas: regla Sigma, consulta KQL/Splunk, firma YARA.
- Huecos: qué no se pudo ver y por qué (captura parcial, retención, sensor).

## 8. Errores típicos

- **Empezar por IOCs**: sin hipótesis, el análisis se agota en la primera lista.
- **Zona horaria**: mezclar local y UTC desplaza la cadena y rompe la correlación.
- **Una sola fuente**: un 7045 sin el 4624 asociado no prueba quién entró.
- **Confundir ausencia con inexistencia**: que no haya evento no significa que no ocurriera; puede faltar telemetría.
- **Volcar conclusiones sin ruta**: sin ruta y hora, la conclusión no es reproducible.

## 9. Detección y mejora

- Convertir cada hallazgo en una regla y probarla con el propio caso.
- Medir cobertura por técnica (ATT&CK) y por fuente; detectar el hueco antes que el atacante.
- Retención y dimensionado: una captura incompleta limita la investigación; el endpoint debe cubrir lo que la red no ve.

MITRE: T1569.002, T1105, T1021.001, T1003.001. Referencias: SANS FOR500, documentación de Eric Zimmerman y ATT&CK.
