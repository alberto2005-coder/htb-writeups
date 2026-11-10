---
sherlock: Heist
domain: DFIR
difficulty: Hard
platform: Hack The Box
evidence: Correo, PCAP y adquisición KAPE parcial de un equipo Windows
tools: [EvtxECmd, PECmd, MFTECmd, SrumECmd, Wireshark, Timeline Explorer]
state: Active
tags: [dfir, phishing, redline, pcap, srum, mft, t1566.001]
---

# Heist — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Active. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un empleado de una empresa de seguros abre un correo sobre una supuesta colaboración. Días después, el equipo de Blue Team recibe un aviso de la plataforma de correo: hay credenciales de la víctima a la venta. Se entrega el correo original, una captura de red y una adquisición parcial del disco.

## Evidencias

- `Email.eml`: mensaje recibido por la víctima.
- `Heist.pcapng`: captura de red del segmento del empleado.
- `Kape_Acquisition.zip`: ~917 ficheros, copia parcial de `C:\` (hives, `$MFT`, Prefetch, perfiles, `SRUDB.dat`).

```bash
sha256sum Email.eml Heist.pcapng Kape_Acquisition.zip
```

## Investigación

### 1. Inventario y triaje

Tres preguntas guía: cuándo entró el correo, qué descargó el usuario y qué salió de la red. El `.eml` fija la hora con la cabecera `Received` (UTC) y el dominio de descarga; el PCAP dice si hubo C2; la adquisición pone el resto.

```bash
grep -iE '^(Received|From|Return-Path|Message-ID):' Email.eml
```

El mensaje llega el **2023-04-11 08:55:22 UTC** y el enlace de descarga apunta a `doc-0s-5g-docs.googleusercontent.com` (Google Docs), un salto que evita el filtro de URLs corporativo. El ZIP descargado es `Forela-Partnership.zip`.

### 2. Línea temporal

El historial de Chrome es una SQLite con dos tablas útiles, `downloads` y `download_url_chains`; `last_visit_time` está en formato WebKit (microsegundos desde 1601-01-01):

```bash
sqlite3 "C/Users/<user>/AppData/Local/Google/Chrome/User Data/Default/History" \
  "select target_path, tab_url, datetime(last_visit_time/1000000-11644473600,'unixepoch') from downloads;"
```

La descarga del ZIP queda a las **10:19:24**. El Prefetch confirma la ejecución del señuelo:

```bash
PECmd.exe -f "C/Windows/Prefetch/PARTNERSHIP.PDF.EXE-CCA24020.pf" --csv out --csvf pecmd.csv
MFTECmd.exe -f '$MFT' --csv out --csvf mft.csv
```

`Partnership.pdf.exe` se ejecuta a las **10:20:06** y deja caer `SI168290.EXE`, `UN598654.EXE` y luego `PRO5093.EXE`, `QU2705.EXE`: nombres aleatorios de seis caracteres, típicos de un *dropper*.

### 3. Artefacto clave

En el PCAP, el flujo HTTP hacia `176.113.115.145:4125` contiene `http://tempuri.org/Entity/Id1`, la firma de serialización de **RedLine Stealer**. El proceso que exfiltra es:

```text
C:\Users\<user>\AppData\Local\Temp\IXP001.TMP\qu2705.exe   (PID 3924)
```

El detalle que cierra el caso no está en el PCAP sino en **SRUM**: el volumen de datos enviados por ese PID.

```bash
SrumECmd.exe -f "C/Windows/System32/SRU/SRUDB.dat" -r "C/Windows/System32/config/SOFTWARE" --csv out
```

`BytesSent` = **107059** para ese proceso, coherente con lo capturado y con la exfiltración de credenciales.

## Conclusiones

- Entrada por phishing con enlace a Google Docs y ZIP con ejecutable de doble extensión.
- RedLine robó credenciales del navegador (incluido un token de Discord) y las envió por HTTP a `176.113.115.145:4125`.
- El PCAP da el destino; SRUM da el volumen real, que la captura sola no demuestra.

## Lecciones

- Un enlace a `googleusercontent.com` no es "tráfico de Google": hay que mirar la ruta y el fichero descargado.
- El historial de Chrome en WebKit necesita la conversión `last_visit_time/1000000-11644473600`; sin ella la línea temporal no cuadra.
- Prefetch + MFT dan ejecución y creación de ficheros; SRUM añade bytes enviados por proceso, que es la prueba de exfiltración.
- `tempuri.org/Entity/Id1` es una firma de familia, no ruido de un servicio legítimo.

## Mitigaciones y detección

- Bloquear ejecutables desde rutas de usuario (`AppData\Local\Temp`) y adjuntos con doble extensión.
- Proxy con inspección de URL completa y bloqueo de descargas desde dominios de almacenamiento no aprobados.
- Detección: Sysmon 1 con `*.pdf.exe`, creación de ficheros de seis caracteres en `Temp`, conexiones a IPs sin dominio con `POST` a `/rj...`, y picos de `BytesSent` en SRUM para procesos de usuario.
- Forzar la rotación de credenciales guardadas en el navegador tras un incidente de este tipo.

MITRE: T1566.001 (spearphishing attachment), T1204.002 (malicious file), T1555.003 (credentials from web browsers), T1041 (exfiltration over C2), T1071.001 (web protocols).

## Referencias

- <https://mwalkowski.com/post/sherlock-heist>
- <https://github.com/EricZimmerman/Srum>
- <https://learn.microsoft.com/en-us/windows/win32/sysinfo/srum>
- <https://www.ired.team/offensive-security/credential-access-and-credential-dumping>
