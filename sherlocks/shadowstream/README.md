---
sherlock: ShadowStream
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, loader, multi-stage, c2, persistence]
---

# ShadowStream — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Loader multicapa que descarga un payload desde un C2, lo ejecuta en memoria y establece persistencia. El análisis de la muestra, la red y el host reconstruye cada etapa.

## Escenario

Un equipo muestra un proceso de baja reputación y tráfico periódico. Se entrega la muestra inicial y artefactos para identificar el payload final y su persistencia.

## Artefactos

- Loader PE y recursos.
- PCAP/TLS y logs de proxy.
- Memoria y procesos.
- `Run`, tareas y servicios.

## Metodología

1. Se analiza el loader con DIE/CAPA y se localizan URLs.
2. Se revisa la configuración y el user-agent.
3. Se captura el segundo stage en red o memoria.
4. Se identifica la técnica de ejecución (inyección, `rundll32`, `regsvr32`).
5. Se documentan persistencia e IOCs.

```bash
capa -vv loader.exe
vol.py -f mem.raw pstree
vol.py -f mem.raw netscan
```

## Preguntas tipo

- ¿Cuántas etapas tiene la cadena?
- ¿Qué URL descarga el segundo stage?
- ¿Dónde se ejecuta el payload?
- ¿Cómo persiste?
- ¿Qué C2 usa el payload final?

## Herramientas

`CAPA`, `Detect It Easy`, `Volatility`, `Wireshark`, `Procmon`.

## Evidencia y redacción

Se conservan hashes, capturas y regiones de memoria con IPs/dominios redactados.

## Lecciones aprendidas

- Los loaders separan descarga y ejecución.
- La memoria conserva el payload si el archivo se borra.
- La persistencia puede instalarse en la segunda etapa.
- El tráfico periódico ayuda a encontrar el C2.

## Detección

- Alertar de procesos que descargan y ejecutan en memoria.
- Vigilar `rundll32`/`regsvr32` con URLs.
- Correlacionar conexiones periódicas.
- Aplicar YARA en memoria y disco.

## Referencias

- <https://app.hackthebox.com/sherlocks/ShadowStream>
- <https://attack.mitre.org/techniques/T1105/>
- <https://attack.mitre.org/techniques/T1055/>
