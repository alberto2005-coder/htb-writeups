---
sherlock: Backdoor
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, iis, webshell, persistence, evtx]
---

# Backdoor — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un servidor IIS comprometido ejecuta un webshell y deja un mecanismo de persistencia. Se reconstruye el acceso inicial con logs HTTP, se localiza el archivo malicioso por MFT y se confirma la ejecución con EVTX y prefetch.

## Escenario

El equipo de respuesta detecta tráfico anómalo hacia un servidor web Windows. Se entregan logs de IIS, EVTX y una imagen parcial del sistema para determinar cómo entró el atacante y qué dejó atrás.

## Artefactos

- Logs de IIS (`W3SVC`).
- EVTX de Security, System y PowerShell.
- `$MFT`, prefetch y `Amcache`.
- Directorio `wwwroot` y archivos temporales.

## Metodología

1. Se identifican peticiones `POST` con parámetros sospechosos y user-agents raros.
2. Se buscan archivos creados en `wwwroot` y se comparan hashes con la línea base.
3. Se revisan eventos 4688, 7045 y 4104 alrededor de la primera petición.
4. Se confirma la ejecución del webshell con prefetch/Amcache.
5. Se enumeran claves `Run`, servicios y tareas creadas después.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
```

## Preguntas tipo

- ¿Qué URI recibió el primer `POST` malicioso?
- ¿Qué archivo se creó en el webroot?
- ¿Qué proceso ejecutó el webshell?
- ¿Qué mecanismo de persistencia se añadió?
- ¿Qué cuenta quedó comprometida?

## Herramientas

`EvtxECmd`, `MFTECmd`, `Timeline Explorer`, `PECmd`, `IIS Log Parser`.

## Evidencia y redacción

Se conservan capturas de las peticiones, rutas y línea temporal con IPs, usuarios y nombres de archivo redactados.

## Lecciones aprendidas

- Los logs de IIS permiten reconstruir el acceso inicial.
- Un archivo nuevo en `wwwroot` es señal de webshell.
- La persistencia puede sobrevivir al reinicio del servicio web.
- La correlación temporal evita atribuciones erróneas.

## Detección

- Alertar de `POST` a extensiones ejecutables en `wwwroot`.
- Vigilar creación de archivos en directorios web.
- Correlacionar 4688 con peticiones HTTP.
- Revisar servicios y tareas creadas tras el incidente.

## Referencias

- <https://app.hackthebox.com/sherlocks/Backdoor>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://attack.mitre.org/techniques/T1547/001/>
