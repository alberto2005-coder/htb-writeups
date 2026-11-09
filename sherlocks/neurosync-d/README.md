---
sherlock: NeuroSync-D
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, medical-device, timeline, lateral-movement]
---


# NeuroSync-D — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

El fabricante de un dispositivo médico conectado (interfaz neuronal) detecta actividad anómala en la estación de un técnico. Se entrega un conjunto de artefactos del endpoint y logs de red; hay que determinar cómo se accedió, qué se manipuló y si el incidente llegó a otros sistemas.

## Evidencias

- Artefactos del endpoint: registro, `Prefetch`, `Amcache`, historial de PowerShell.
- Logs de autenticación y de red del segmento de laboratorio.
- Inventario de dispositivos y software del fabricante.

## Investigación

### 1. Punto de entrada

```bash
PECmd.exe -d triage/Prefetch --csv out/
grep -i "powershell" out/*.csv | head -20
```

Los indicadores típicos son un ejecutable descargado a `Downloads` seguido de un `powershell -enc` en la misma ventana de tiempo. El historial de consola (`ConsoleHost_history.txt`) suele conservar el comando completo.

### 2. Qué se hizo con el dispositivo

Se cruza la hora de ejecución con los logs del software clínico: lecturas de configuración, exportaciones de datos de pacientes o cambios de firmware. En este escenario lo relevante no es el malware sino el **acceso a datos regulados**.

### 3. Alcance

```bash
grep -i "4624\|4625\|4648" Security.evtx | head
```

Se revisan logins tipo 3/10 desde el host comprometido hacia otros equipos y el uso de credenciales de servicio. El alcance se cierra con los sistemas que compartían cuenta.

## Conclusiones

- Compromiso de una estación de laboratorio con acceso a datos de dispositivos médicos.
- Movimiento lateral limitado por segmentación, pero con exposición de información sensible.
- El impacto se mide en cumplimiento (datos de salud), no solo en flags.

## Lecciones

- En entornos regulados, el análisis empieza por qué datos se tocaron, no por qué binario se ejecutó.
- La segmentación de red es lo que separa un incidente de un desastre cuando el endpoint cae.
- Documentar la cadena de custodia y los hashes es parte del entregable.
