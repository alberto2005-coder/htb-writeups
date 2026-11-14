---
sherlock: CrashDump
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, windows, crash-dump, volatility, memory]
---

# CrashDump — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un servidor Windows se reinició de forma inesperada durante la noche. Se conservó el volcado de memoria y parte de los artefactos del sistema. Se pide determinar si el fallo fue causado por un proceso malicioso y reconstruir la actividad previa.

## Evidencias

- `MEMORY.DMP` o un volcado completo del sistema.
- `$MFT`, `$J` y copia de los EVTX.
- Listado de procesos y conexiones del momento del fallo.

```bash
sha256sum MEMORY.DMP
vol -f MEMORY.DMP windows.info
```

## Investigación

### 1. Inventario y triaje

Se identifica la versión de Windows, la arquitectura y el momento del volcado. Después se listan procesos, módulos y conexiones para localizar nombres fuera de lo esperado.

```bash
vol -f MEMORY.DMP windows.pslist
vol -f MEMORY.DMP windows.pstree
vol -f MEMORY.DMP windows.netscan
```

### 2. Línea temporal

Se cruzan los tiempos de arranque, los eventos de servicio y las marcas de los procesos. Un proceso con nombre legítimo pero ruta en `%TEMP%` o `%APPDATA%` es sospechoso. Las conexiones salientes al mismo destino refuerzan la hipótesis de C2.

```bash
vol -f MEMORY.DMP windows.cmdline
vol -f MEMORY.DMP windows.malfind
```

### 3. Artefacto clave

El análisis de `malfind` muestra regiones con permisos `PAGE_EXECUTE_READWRITE` y cabeceras MZ sin respaldo en disco. Se extrae el contenido, se calcula su hash y se compara con los archivos del sistema. El proceso inyectado y su línea de comandos explican el reinicio.

## Conclusiones

- El fallo no fue un simple error de hardware.
- Un proceso obtuvo ejecución y se comunicó con infraestructura externa.
- El volcado conserva evidencia suficiente para identificar el payload y el C2.
- Los EVTX permiten acotar la ventana de persistencia.

## Lecciones

- Un crash dump es evidencia volátil de alto valor.
- `malfind` no confirma malware por sí solo; hay que correlacionar.
- La ausencia de un archivo en disco no implica que el código no existiera.
- Centralizar los volcados y proteger su cadena de custodia.

## Referencias

- <https://www.hackthebox.com/sherlocks/CrashDump>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1055/>
