---
sherlock: <Nombre>
domain: <DFIR|SOC|Malware Analysis|Threat Intelligence|Cloud>
difficulty: <Very Easy|Easy|Medium|Hard|Insane>
platform: Hack The Box
state: <Active|Retired>
tags: [dfir, <pcap|memory|evtx|registry|malware>]
---

# <Nombre> — Hack The Box

[🇬🇧 English](sherlock-template.en.md) | **Español**

> **Estado:** <Retired, ficha publicable | Active, borrador privado.>
> Ficha de investigación; sin respuestas literales de la plataforma ni datos reales.

## Escenario

<Dos o tres frases con el contexto del incidente y qué se pide.>

## Evidencias

- <Fichero y qué es.>
- <Fichero y qué es.>

```bash
sha256sum <evidencia>       # anotar hashes antes de analizar
```

## Investigación

### 1. Inventario y triaje

<Qué se abre primero y por qué. Comandos concretos.>

```bash
<comando>
```

### 2. Línea temporal

<Ejecución, logons, conexiones. Qué fuente da la hora fiable y en qué zona horaria.>

### 3. Artefacto clave

<El artefacto que resuelve el caso: ruta exacta, por qué importa, qué prueba.>

## Conclusiones

- <Qué pasó, en orden.>
- <Qué se llevaron o qué se modificó.>
- <IOC principales.>

## Lecciones

- <Qué habría detectado esto antes.>
- <Mitigación concreta.>
- <Qué artefacto falta en la organización.>
