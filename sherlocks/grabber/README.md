---
sherlock: Grabber
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, infostealer, static-analysis, dynamic-analysis, iocs]
---

# Grabber — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni respuestas literales.

## TL;DR

Análisis de un malware tipo infostealer/grabber. Se combinan triaje estático, ejecución controlada y análisis de red para identificar qué credenciales y navegadores targeting, dónde escribe los datos y cómo los exfiltra. El objetivo es producir IOCs y una regla de detección.

## Escenario

Un usuario reporta robo de cuentas tras ejecutar un archivo descargado. Se entrega una muestra o artefactos de ejecución y se solicita determinar capacidades, persistencia y destino de los datos.

## Artefactos

- Muestra PE (posiblemente empaquetada).
- Logs de proceso y red.
- Artefactos de navegador/credenciales.
- Persistencia en registro o tareas.
- PCAP o logs de proxy.

## Metodología

1. Se calculan hashes y se revisan cabeceras, imports y strings.
2. Se identifica el empaquetado y se desofusca si es necesario.
3. Se ejecuta en una VM aislada con monitoreo de proceso, registro y red.
4. Se observan rutas de navegadores, wallets y credenciales.
5. Se localiza el C2, el formato de exfiltración y la persistencia.
6. Se generan IOCs y reglas Sigma/YARA.

```bash
file sample.exe
strings -n 8 sample.exe | head
pefile sample.exe
```

## Preguntas tipo

- ¿Qué familias de navegadores y wallets busca?
- ¿Dónde almacena los datos antes de enviarlos?
- ¿Qué dominio/IP usa para exfiltrar?
- ¿Qué mecanismo de persistencia crea?
- ¿Qué técnicas MITRE ATT&CK aplica?

## Herramientas

`PEStudio`, `Detect It Easy`, `Ghidra`, `x64dbg`, `Procmon`, `Wireshark`, `YARA`.

## Evidencia y redacción

Se conservan hashes, capturas de strings y tráfico con dominios y rutas redactados. No se publican credenciales, claves ni la flag.

## Lecciones aprendidas

- Los infostealers priorizan navegadores y wallets.
- La ejecución dinámica confirma rutas y C2.
- El empaquetado no impide el análisis de strings/imports.
- Los IOCs deben incluir comportamiento, no solo hashes.

## Detección

- Alertar de acceso masivo a `Login Data`, `Cookies` y wallets.
- Vigilar procesos que leen perfiles de navegador.
- Bloquear C2 por dominio/IP y proxy.
- Detectar persistencia en `Run` y tareas programadas.

## Referencias

- <https://app.hackthebox.com/sherlocks/Grabber>
- <https://attack.mitre.org/techniques/T1555/003/>
- <https://attack.mitre.org/techniques/T1041/>
