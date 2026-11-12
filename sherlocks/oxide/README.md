---
sherlock: Oxide
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, memory, process-injection, volatility, malware]
---

# Oxide — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un volcado de memoria Windows contiene un proceso inyectado y conexiones C2. Se usan `pstree`, `malfind`, `netscan` y `dlllist` para identificar la inyección, el payload y la persistencia.

## Escenario

Un host muestra lentitud y conexiones salientes intermitentes. Se entrega un volcado de memoria y se solicita identificar el proceso malicioso y su canal de mando.

## Artefactos

- Memoria completa (`memdump.mem`/`.raw`).
- `pstree`, `malfind`, `netscan`.
- `dlllist`, `handles`, `cmdline`.

## Metodología

1. Se identifica el perfil con `imageinfo`.
2. Se revisan procesos huérfanos y relaciones padre-hijo anómalas.
3. `malfind` localiza regiones ejecutables sin respaldo en disco.
4. `netscan` correlaciona conexiones con procesos.
5. Se extraen cadenas y se calculan hashes del payload.

```bash
vol.py -f memdump.mem imageinfo
vol.py -f memdump.mem --profile=Win10x64_19041 pstree
vol.py -f memdump.mem --profile=Win10x64_19041 malfind
vol.py -f memdump.mem --profile=Win10x64_19041 netscan
```

## Preguntas tipo

- ¿Qué proceso está inyectado?
- ¿Qué DLL o región es anómala?
- ¿A qué C2 se conecta?
- ¿Qué proceso lo lanzó?
- ¿Hay persistencia en memoria?

## Herramientas

`Volatility 2/3`, `MemProcFS`, `strings`, `YARA`.

## Evidencia y redacción

Se conservan capturas de procesos, regiones y conexiones con IPs, usuarios y rutas redactados.

## Lecciones aprendidas

- La inyección deja regiones ejecutables sin archivo de respaldo.
- `netscan` une proceso y conexión.
- Los procesos huérfanos delatan malware.
- La memoria complementa el disco cuando falta el binario.

## Detección

- Alertar de procesos con regiones `PAGE_EXECUTE_READWRITE`.
- Monitorizar conexiones de procesos no esperados.
- Correlacionar inyección con acceso a red.
- Aplicar YARA en memoria.

## Referencias

- <https://app.hackthebox.com/sherlocks/Oxide>
- <https://attack.mitre.org/techniques/T1055/>
- <https://github.com/volatilityfoundation/volatility3>
