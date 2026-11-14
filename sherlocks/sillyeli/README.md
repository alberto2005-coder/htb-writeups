---
sherlock: SillyEli
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, srum, ese, powershell, scheduled-tasks]
---

# SillyEli — Hack The Box (Sherlock)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un servidor Windows muestra actividad de red y procesos fuera de horario. Se entrega una colección KAPE y se pide identificar el ejecutable, la persistencia y el volumen exfiltrado.

## Evidencias

- `SRUM` (`SRUDB.dat`) y `Windows.edb`.
- Tareas programadas, servicios y PowerShell.
- `$MFT`, `Prefetch` y logs de Security.

```bash
sha256sum evidence/*
find evidence -iname 'SRUDB.dat' -o -iname 'Windows.edb'
```

## Investigación

### 1. Consumo y red

`SrumECmd` extrae por proceso bytes enviados/recibidos y tiempos. Un proceso con tráfico alto en una ventana concreta orienta la búsqueda.

```bash
SrumECmd.exe -f SRUDB.dat --csv srum
```

### 2. Ejecución y persistencia

`PECmd` confirma la ejecución; las tareas programadas y los servicios explican la persistencia. `Windows.edb` puede conservar rutas y búsquedas del usuario.

```bash
PECmd.exe -d Prefetch --csv prefetch
```

### 3. PowerShell y alcance

Se revisan 4103/4104 y transcripciones. El comando de descarga o compresión se cruza con SRUM y con la MFT para estimar qué se empaquetó y envió.

## Conclusiones

- SRUM aporta volumen y ventana temporal.
- La persistencia se confirma con tareas o servicios.
- PowerShell documenta el comando y el usuario.
- La estimación de exfiltración se apoya en dos fuentes.

## Lecciones

- SRUM es útil cuando faltan logs de red.
- El ESE puede estar bloqueado; trabajar sobre una copia.
- Las tareas programadas dejan rastro en varios artefactos.
- La atribución de volumen es una estimación, no una certeza.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/Srum>
- <https://attack.mitre.org/techniques/T1053/005/>
