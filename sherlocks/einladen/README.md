---
sherlock: Einladen
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Retired
tags: [dfir, windows, html-smuggling, hta, dll-sideloading, procmon, pcap]
---

# Einladen — Hack The Box Sherlock

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (04/04/2024). Ficha de referencia; no jugada en este perfil.
> Sin flags, hashes ni dominios de C2 reales.

## TL;DR

Un correo entrega un `downloader.html` que genera un ZIP en el navegador mediante **HTML smuggling**. El ZIP contiene un señuelo PDF, un HTA, un ejecutable legítimo y dos DLL para **DLL side-loading**. La ejecución encadena `sheet.hta` → `msoev.exe` → DLL maliciosa → stager de Empire. El `Logfile.PML` de Procmon y el `msoev.pcapng` permiten reconstruir la ejecución y el canal de mando.

## Artefactos

| Artefacto | Papel |
|---|---|
| `downloader.html` | Dropper HTML; construye el ZIP en memoria |
| `sheet.hta` | Lanzador; ejecuta el binario señuelo |
| `invoice.pdf` | Documento de distracción |
| `msoev.exe` | Ejecutable legítimo usado como señuelo |
| `mso.dll` | DLL maliciosa cargada por side-loading |
| `AppVIsvSubsystems64.dll` | DLL de soporte/abuso de búsqueda |
| `EmpireClient.exe` | Cliente/stager de Empire |
| `unc.js` | Script de puente hacia el recurso remoto |
| `Logfile.PML` | Captura de Procmon |
| `msoev.pcapng` | Tráfico de red del execution |

## 1. Triaje del correo y del dropper

Se empieza por la fecha, el remitente y el nombre del adjunto. `downloader.html` no descarga un binario directamente: contiene JavaScript ofuscado que decodifica un blob Base64, crea un `Blob` y fuerza la descarga de un ZIP. El navegador nunca solicita el ZIP al servidor, por lo que un proxy que solo registra URLs no lo ve.

```bash
file downloader.html
grep -oE '[A-Za-z0-9+/=]{100,}' downloader.html | head
```

El ZIP resultante se extrae en una carpeta de trabajo. Se calculan hashes para el registro, pero no se publican.

## 2. Cadena de ejecución

El orden observado en Procmon es:

```text
explorer.exe
  └─ mshta.exe sheet.hta
       └─ msoev.exe
            ├─ mso.dll
            ├─ AppVIsvSubsystems64.dll
            └─ EmpireClient.exe
```

- El HTA se ejecuta con `mshta.exe`, un binario de confianza para Windows.
- `msoev.exe` es legítimo y se coloca junto a las DLL maliciosas para que la búsqueda de dependencias cargue `mso.dll` antes que la versión del sistema.
- `AppVIsvSubsystems64.dll` actúa como puente o proxy de exportaciones.
- El PDF abierto por el usuario es el señuelo que justifica la ejecución.

En Procmon se filtran `Process Name is msoev.exe` y `Operation is Load Image`; ahí se ve qué DLL se carga y desde qué ruta. También se revisan `CreateFile`, `RegSetValue` y `TCP Send/Receive`.

## 3. Red

`msoev.pcapng` se abre en Wireshark. Filtros útiles:

```text
dns
http.request
tls.handshake.extensions_server_name
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Se identifica el primer beacon, la periodicidad y el host de C2. No se copian dominios ni IPs reales en la ficha; se describen como `<C2_HOST>` y `<C2_IP>`. El `User-Agent` y la ruta del POST son más útiles que la IP, que puede rotar.

## 4. Persistencia y alcance

- `EmpireClient.exe` se copia a una ruta de usuario y se lanza como hijo de `msoev.exe`.
- Se revisan Run keys, tareas programadas y servicios creados en la ventana temporal.
- `unc.js` puede actuar como puente para invocar un recurso UNC; se comprueba si genera tráfico SMB.
- Se buscan otros equipos con el mismo `downloader.html` o el mismo hash del ZIP.

## 5. Línea temporal

| Hora (UTC) | Evento |
|---|---|
| T0 | Recepción del correo con `downloader.html` |
| T0+1m | El navegador genera y descarga el ZIP |
| T0+2m | `mshta.exe` ejecuta `sheet.hta` |
| T0+2m | `msoev.exe` carga `mso.dll` |
| T0+3m | Primer beacon de `EmpireClient.exe` |
| T0+5m | Persistencia y copia del payload |

## Lecciones aprendidas

- HTML smuggling evade la inspección de adjuntos porque el archivo se construye en el cliente.
- El side-loading usa un ejecutable firmado y una DLL con el mismo nombre que la esperada.
- Procmon y pcap se complementan: uno da el proceso, el otro la red.
- Un PDF señuelo no es el payload; sirve para que el usuario no sospeche.
- La atribución de “Empire” se apoya en el binario y en el patrón de beacon, no en una sola cadena.

## Mitigaciones y detección

- Bloquear `mshta.exe` y ejecutables desde rutas de usuario con reglas de AppLocker/WDAC.
- Alertar de DLL cargadas desde `Downloads`, `Temp` o `AppData` por procesos firmados.
- Inspeccionar HTML con JavaScript que genere blobs y descargas; no solo adjuntos PE.
- Detección: `mshta` → `msoev` → `EmpireClient`, conexiones periódicas y creación de tareas.
- Aislar el host, rotar credenciales y buscar el mismo dropper en el correo.

MITRE: T1027.006, T1218.005, T1574.002, T1071.001.

## Referencias

- <https://0xdf.gitlab.io/2024/05/02/htb-sherlock-einladen.html>
- <https://attack.mitre.org/techniques/T1027/006/>
- <https://attack.mitre.org/techniques/T1574/002/>
