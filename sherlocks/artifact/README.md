---
sherlock: Artifact
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, mft, archives, timeline, exfiltration]
---

# Artifact — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Se investiga la creación y salida de un archivo comprimido con datos sensibles. MFT, prefetch, LNK y logs de red permiten reconstruir qué se comprimió, cuándo y cómo salió del host.

## Escenario

Una organización sospecha que un empleado empaquetó información antes de abandonar la empresa. Se entrega una imagen parcial y se pide reconstruir la preparación y la exfiltración.

## Artefactos

- `$MFT` y `$UsnJrnl`.
- Prefetch, LNK y jumplists.
- Logs de firewall/proxy.
- Historial de PowerShell.

## Metodología

1. Se buscan archivos `.zip`/`.7z`/`.rar` creados en el periodo.
2. Se revisan timestamps MFT y USN para el orden de creación.
3. Se confirma la ejecución del compresor con prefetch.
4. Se revisan LNK/jumplists para archivos de origen.
5. Se correlaciona con conexiones salientes y nubes.

```bash
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Preguntas tipo

- ¿Qué archivo comprimido se creó?
- ¿Qué archivos lo componen?
- ¿Qué herramienta se usó?
- ¿Cuándo se creó y modificó?
- ¿Se subió a un servicio externo?

## Herramientas

`MFTECmd`, `PECmd`, `LECmd`, `Timeline Explorer`, `Wireshark`.

## Evidencia y redacción

Se conservan capturas de la línea temporal y hashes con nombres de usuario, rutas y destinos redactados.

## Lecciones aprendidas

- La MFT conserva creación, modificación y acceso.
- El compresor deja rastro en prefetch.
- Los LNK revelan los archivos seleccionados.
- La exfiltración necesita correlación de red.

## Detección

- Alertar de compresión masiva de documentos.
- Vigilar subidas a almacenamiento personal.
- Correlacionar MFT con tráfico saliente.
- Revisar accesos fuera de horario.

## Referencias

- <https://app.hackthebox.com/sherlocks/Artifact>
- <https://attack.mitre.org/techniques/T1560/001/>
- <https://attack.mitre.org/techniques/T1048/>
