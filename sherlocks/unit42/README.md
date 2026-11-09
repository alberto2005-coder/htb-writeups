---
sherlock: Unit42
domain: DFIR / Malware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, sysmon, evtx, ultravnc, timestomp, dropbox, c2]
---

# Unit42 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un host Windows (`DESKTOP-887GK2L`, usuario `CyberJunkie`) tiene un ejecutable sospechoso. Solo se entrega **un log de Sysmon**: hay que reconstruir la infección inspirada en la campaña de UltraVNC backdoor que publicó Palo Alto Unit 42.

## Evidencias

```text
sysmon.evtx
```

## Investigación

### 1. Del evento suelto a la línea temporal

```powershell
Get-WinEvent -Path .\sysmon.evtx | Group-Object Id | Sort-Object Count -Descending
```

Los `EventID` de Sysmon que importan aquí:

| ID | Evento | Para qué sirve |
|---|---|---|
| 1 | ProcessCreate | binario, línea de comandos, proceso padre, hashes |
| 2 | FileCreateTime changed | **timestomping** |
| 3 | NetworkConnect | IP/puerto de salida (C2) |
| 5 | ProcessTerminated | fin del dropper |
| 11 | FileCreate | ficheros que deja en disco |
| 22 | DNSQuery | resolución de dominios |

### 2. El binario y su disfraz

Se filtra `EventID 1` y se ordena por hora. El proceso malicioso usa **doble extensión** (`*.exe.exe`) y se ejecuta desde la carpeta de descargas del usuario, con un padre que es el explorador: ejecución manual, no servicio.

El nombre del fichero se corrobora con `EventID 11`: pocos ficheros creados, todos alrededor del mismo minuto.

### 3. Evasión

- **`EventID 2`**: alguien cambió la fecha de creación del binario. Es timestomping y explica por qué el fichero «parece viejo».
- **`EventID 22`**: consulta DNS previa a una conexión. Los droppers resuelven un dominio de control para comprobar que hay internet antes de hablar con el C2 real.
- **`EventID 5`**: el dropper termina justo después de dejar el implante. Un proceso de vida corta que crea ficheros y muere es firma de *dropper*, no de malware residente.

### 4. El implante

La persistencia no es un servicio nuevo con nombre raro, sino una **variante backdoorizada de UltraVNC**: se instala como servicio legítimo y pasa desapercibido. Se localiza por la ruta del ejecutable y por el `EventID 1` posterior, no por firma.

El origen de la descarga se identifica con la URL del evento de creación y con el dominio de `EventID 22`: un servicio de almacenamiento en la nube (Dropbox), que evade filtros de correo.

## Conclusiones

- Entrega: enlace a Dropbox, ejecución manual del usuario.
- Ejecución: binario con doble extensión y timestomping previo.
- Persistencia: UltraVNC modificado como servicio con apariencia legítima.
- C2: conexión saliente tras una consulta DNS de comprobación.

## Lecciones

- Un único canal de Sysmon basta para una cronología completa si se cruzan los IDs 1/2/3/5/11/22.
- El timestomping se detecta por la divergencia entre `$STANDARD_INFORMATION` y el evento 2, no mirando fechas a ojo.
- El DLL/EXE sideloading y los servicios «legítimos» backdoorizados no se cazan por firma: se cazan por ruta y por hora.
