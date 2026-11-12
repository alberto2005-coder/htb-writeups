---
sherlock: SmartyPants
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, rdp, smartscreen, timeline]
---

# SmartyPants — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; no se descargaron las evidencias originales.

## TL;DR

Un servidor de ficheros Windows fue accedido por RDP, se instalaron utilidades de borrado y exfiltración, y después se limpiaron los logs. Los EVTX permiten reconstruir el acceso inicial (1149), la ejecución de herramientas, la copia de datos y el borrado de logs (1102). SmartScreen aporta contexto sobre descargas y ejecutables.

## Escenario

El CTO guarda archivos críticos en un servidor Windows separado del dominio. Un intruso accede por RDP, instala utilidades, sustrae información y la elimina. La organización recibe una extorsión y solicita un triaje forense.

## Artefactos

- Colección de EVTX del sistema comprometido.
- Logs de SmartScreen.
- Metadatos de ejecución y línea temporal.
- Sin imagen de disco completa.

## Metodología

1. Se inventarían los canales EVTX y se convierten a JSON/CSV con `EvtxECmd` o `evtx_dump`.
2. Se busca el evento 1149 de Terminal Services para el primer RDP correcto.
3. Se revisan `Microsoft-Windows-SmartScreen` y los eventos de ejecución para identificar binarios descargados o instalados.
4. Se localizan utilidades de borrado (`Everything`, `File Shredder`) y se confirma el evento 1102 de limpieza de logs.
5. Se construye una línea temporal con `Timeline Explorer` y se responde a las preguntas del Sherlock.

```bash
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
```

## Preguntas tipo

- ¿Cuándo se produjo el primer acceso RDP?
- ¿Qué utilidad se usó para localizar archivos?
- ¿Qué herramienta borró los datos?
- ¿A qué hora se limpiaron los logs?
- ¿Qué ejecutable de SmartScreen está relacionado con la intrusión?

## Herramientas

`EvtxECmd`, `Timeline Explorer`, `jq`, `grep`, `Chainsaw`.

## Evidencia y redacción

Se conservan capturas de los eventos y de la línea temporal, con nombres de usuario, IP y rutas sensibles redactados. No se publican respuestas literales ni la flag.

## Lecciones aprendidas

- El evento 1149 identifica accesos RDP correctos.
- SmartScreen ayuda a reconstruir descargas y ejecuciones.
- El evento 1102 confirma la limpieza de logs, pero no borra los EVTX ya copiados.
- La ausencia de logs clásicos no impide reconstruir la actividad.

## Detección

- Alertar de 1149 desde IPs no habituales.
- Correlacionar 1102 con actividad de borrado y exfiltración.
- Vigilar la instalación de `Everything` y herramientas de shredding.
- Centralizar logs antes de que el atacante pueda limpiarlos.

## Referencias

- <https://app.hackthebox.com/sherlocks/SmartyPants>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-1102>
- <https://attack.mitre.org/techniques/T1070/001/>
