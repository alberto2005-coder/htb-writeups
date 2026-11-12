---
sherlock: BlackEnergy
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, blackenergy, dropper, c2, static-analysis, dynamic-analysis]
---

# BlackEnergy — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Análisis de una muestra asociada a BlackEnergy. Se identifican el dropper, la persistencia, el canal C2 y las capacidades de ejecución remota mediante análisis estático y dinámico controlado.

## Escenario

Se recibe una muestra binaria y artefactos de un host con comunicaciones periódicas. El objetivo es clasificar la familia, documentar el flujo de ejecución y extraer IOCs sin ejecutar la muestra en producción.

## Artefactos

- Binario PE y posibles recursos embebidos.
- PCAP de la comunicación.
- EVTX y claves de persistencia.
- Cadenas, imports y configuración.

## Metodología

1. Se calculan hashes y se identifica el compilador/empaquetador con `pefile` y Detect It Easy.
2. Se revisan imports, secciones y cadenas en busca de URLs, claves y rutas.
3. Se ejecuta en una VM aislada con `procmon`, `procexp` y captura de red.
4. Se documenta el proceso padre, archivos creados, claves `Run` y tráfico.
5. Se extraen IOCs y reglas de detección.

```bash
pefile sample.exe
strings -n 8 sample.exe | less
procmon /quiet
```

## Preguntas tipo

- ¿Qué familia o variante es?
- ¿Qué mecanismo de persistencia usa?
- ¿Cuál es el dominio/IP de C2?
- ¿Qué técnicas de evasión aplica?
- ¿Qué procesos lanza y con qué argumentos?

## Herramientas

`Detect It Easy`, `pefile`, `Procmon`, `Wireshark`, `CAPA`, `YARA`.

## Evidencia y redacción

Se conservan hashes, rutas y capturas de tráfico con dominios, IPs y claves redactados. No se distribuye la muestra.

## Lecciones aprendidas

- El análisis estático acota el comportamiento antes de ejecutar.
- La persistencia y el C2 suelen estar en recursos/configuración.
- El tráfico periódico ayuda a identificar el canal.
- Los IOCs deben validarse en el contexto del incidente.

## Detección

- Buscar creación de servicios/claves `Run` desde procesos no instaladores.
- Bloquear dominios/IPs de C2 conocidos.
- Alertar de conexiones periódicas a destinos nuevos.
- Aplicar YARA sobre binarios y memoria.

## Referencias

- <https://app.hackthebox.com/sherlocks/BlackEnergy>
- <https://attack.mitre.org/software/S0089/>
- <https://github.com/mandiant/capa>
