---
sherlock: TrainingDay
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, macro, dropper, powershell, persistence]
---

# TrainingDay — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Un documento Office con macros descarga y ejecuta un dropper. Se analiza el flujo estático y dinámico para identificar el payload, la persistencia y el canal de salida.

## Escenario

Un usuario abre un documento adjunto y el host empieza a generar tráfico. Se entrega el documento y artefactos de ejecución para reconstruir la cadena.

## Artefactos

- Documento `.docm`/`.xlsm`.
- Macros VBA y cadenas ofuscadas.
- EVTX, prefetch y `%TEMP%`.
- PCAP de la conexión saliente.

## Metodología

1. Se extraen las macros con `olevba`/`oletools`.
2. Se decodifican cadenas y se localiza la URL de descarga.
3. Se identifica el proceso hijo (`powershell`, `mshta`, `rundll32`).
4. Se revisan archivos creados y claves `Run`.
5. Se documentan IOCs y el canal C2.

```bash
olevba document.docm
strings -n 8 payload.bin
```

## Preguntas tipo

- ¿Qué macro se ejecuta al abrir el documento?
- ¿Qué URL descarga el payload?
- ¿Qué proceso lanza el dropper?
- ¿Dónde se guarda y cómo persiste?
- ¿A qué C2 se conecta?

## Herramientas

`oletools`, `CyberChef`, `Procmon`, `Wireshark`, `PEStudio`.

## Evidencia y redacción

Se conservan capturas de macros y hashes con URLs, usuarios y rutas redactados.

## Lecciones aprendidas

- Las macros siguen siendo un vector de entrada.
- La ofuscación VBA se revierte con paciencia.
- El proceso hijo delata la ejecución.
- La persistencia suele estar en `Run` o tareas.

## Detección

- Bloquear macros de Internet.
- Alertar de Office que lanza PowerShell.
- Revisar descargas a `%TEMP%`.
- Aplicar YARA a documentos y payloads.

## Referencias

- <https://app.hackthebox.com/sherlocks/TrainingDay>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://attack.mitre.org/techniques/T1059/001/>
