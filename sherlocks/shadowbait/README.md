---
sherlock: ShadowBait
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Logs de Windows (Sysmon, PowerShell, Security) de un puesto comprometido
tools: [Hayabusa, EvtxECmd, Timeline Explorer, grep]
state: Retired
tags: [dfir, dfir-/-windows]
---


# ShadowBait — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El usuario Steven abre un documento de Office que llega por correo. A partir de ahí el puesto empieza a generar actividad: PowerShell, descargas, acceso a credenciales y persistencia. Se entregan los logs del equipo para reconstruir la cadena.

## Evidencias

- Canales de eventos de Windows: Sysmon, PowerShell (incluido *Script Block Logging*) y Security.

## Investigación

1. **Convertir todo a una línea temporal** — con decenas de miles de eventos, esto es lo que hace viable el análisis:

```bash
hayabusa csv-timeline -d ./logs -o timeline.csv
```

2. **Documento malicioso**: buscar procesos hijos de Office (`WINWORD.EXE`, `EXCEL.EXE`) que no deberían existir.

```text
EventID 1 (Sysmon) | ParentImage ends with WINWORD.EXE
```

3. **Staging**: el documento lanza PowerShell; aparecen descargas (`Net.WebClient`, `Invoke-WebRequest`, `certutil -urlcache`) y ejecución en memoria.

```text
EventID 4104 | ScriptBlockText contains DownloadString
```

4. **C2**: el binario descargado (`OpenDLL.exe`) abre conexión al host atacante; EventID 3 de Sysmon da IP y puerto (`192.168.204.152:8899`).

5. **Acceso a credenciales**: uso de DPAPI sobre datos `PSCredential` guardados; buscar en los comandos `ConvertTo-SecureString`, `Export-Clixml` y rutas `AppData\Roaming\Microsoft\Credentials`.

6. **Persistencia y elevación**: tareas programadas, servicios nuevos, `EventID 7045`, y modificaciones de registro en `Run`/`RunOnce`.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- El *Script Block Logging* (4104) es la mejor fuente para ver qué ejecutó PowerShell y con qué argumentos.
- Un timeline único convierte una investigación de horas en una lectura secuencial.
- DPAPI protege secretos **del usuario**, no de un atacante que ya corre como ese usuario.

## Tropiezos

- **Volumen**: sin CSV previo es fácil perderse; primero filtrar por proceso y por hora.
- **Ruido de actualizaciones**: `svchost`, `OneDrive` y `Teams` generan descargas legítimas; el discriminante es el padre (Office).
- **Zona horaria**: los EVTX guardan UTC; anotar la conversión antes de responder.
