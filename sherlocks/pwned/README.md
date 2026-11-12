---
sherlock: Pwned
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, ransomware, shadow-copies, persistence, timeline]
---

# Pwned — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Un host Windows aparece con archivos renombrados y una nota de rescate. Se reconstruye la ejecución del ransomware, el borrado de copias de sombra y el alcance con EVTX, MFT y registro.

## Escenario

El usuario reporta que no puede abrir documentos y encuentra una nota de rescate. Se entregan artefactos de triaje para identificar el binario, el método de persistencia y los datos afectados.

## Artefactos

- Nota de rescate y archivos renombrados.
- EVTX (4688, 7045, 4104).
- `$MFT`, `$UsnJrnl`, prefetch.
- Claves `Run` y tareas programadas.

## Metodología

1. Se identifica la extensión y la nota; se calcula hash.
2. Se busca el binario en prefetch/MFT y su proceso padre.
3. Se revisan eventos de `vssadmin`, `wbadmin` y PowerShell.
4. Se enumeran servicios/tareas creados antes del cifrado.
5. Se delimita el alcance por timestamps y shares.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Preguntas tipo

- ¿Qué binario cifró los archivos?
- ¿Cómo se ejecutó por primera vez?
- ¿Se borraron copias de sombra?
- ¿Qué cuentas y shares se vieron afectados?
- ¿Existe persistencia activa?

## Herramientas

`EvtxECmd`, `MFTECmd`, `PECmd`, `Timeline Explorer`, `Volatility`.

## Evidencia y redacción

Se conservan capturas de la nota, hashes y línea temporal con usuarios, rutas y claves redactados. No se publica la nota literal.

## Lecciones aprendidas

- La nota y la extensión dan el primer IOC.
- `vssadmin delete shadows` es señal de ransomware.
- Prefetch/MFT localizan el binario aunque se borre.
- La persistencia puede quedar activa tras el cifrado.

## Detección

- Alertar de borrado de copias de sombra.
- Vigilar renombrado masivo y notas `README`.
- Correlacionar 4688 con creación de servicios.
- Aislar el host y preservar memoria antes de limpiar.

## Referencias

- <https://app.hackthebox.com/sherlocks/Pwned>
- <https://attack.mitre.org/techniques/T1486/>
- <https://attack.mitre.org/techniques/T1490/>
