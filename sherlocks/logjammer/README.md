---
sherlock: Logjammer
domain: Log Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, evtx, windows-events, firewall, scheduled-task, powershell, sharphound]
---

# Logjammer — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Evaluación técnica de DFIR: se entregan **cinco canales de eventos** exportados de un único Windows (`DESKTOP-887GK2L`), usado por la cuenta `cyberjunkie`, y hay que reconstruir toda la actividad posterior al compromiso: primer inicio de sesión, reglas de cortafuegos, cambios de auditoría, tareas programadas, PowerShell ejecutado y evidencias destruidas.

## Evidencias

```text
System.evtx
Security.evtx
Powershell-Operational.evtx
Windows Firewall-Firewall.evtx
Windows Defender-Operational.evtx
```

## Investigación

### 1. Lectura y línea base

```bash
EvtxECmd.exe -d ./logs -o out/ --csv out/
```

Con el CSV completo en Timeline Explorer se filtran por `EventID` y se ordenan por tiempo. Conviene fijar la zona horaria antes de responder: los eventos vienen en UTC y muchas preguntas piden hora local.

### 2. Primer acceso y sesión

- **4624** (inicio de sesión correcto) con `LogonType` 2/10 y el usuario `cyberjunkie`: da la hora del primer acceso.
- **4634/4647** cierran la sesión; sirven para separar bloques de actividad.

### 3. Persistencia y configuración

- **4698**: tarea programada creada. El XML embebido trae la ruta del script y la periodicidad. Es el mecanismo que sobrevive al reinicio.
- **4719**: cambio de política de auditoría (alguien se prepara para borrar o evitar logs).
- **2004** en el canal de cortafuegos: regla creada con campos numéricos (`Direction 2` = salida, `Protocol 6` = TCP, `RemotePort 4444`). Traducir los códigos antes de responder; una regla de salida al 4444 es un C2.

### 4. Herramientas y ejecución

- **1116/1117** en Defender: detección y acción sobre una herramienta de reconocimiento de AD (SharpHound). Aunque se cuarentene, la detección delata la intención.
- **4104** en PowerShell Operational: ScriptBlock con el comando real ejecutado. Es la fuente que dice *qué* se ejecutó, no solo que se abrió PowerShell.

### 5. Destrucción de evidencia

- **104** en el canal de cortafuegos: el log fue vaciado. El propio borrado genera el evento que señala el canal manipulado. Cruzarlo con **1102** (Security) si existe.

## Conclusiones

- Actividad *hands-on-keyboard* con persistencia por tarea programada y regla de salida al 4444.
- Reconocimiento de AD con SharpHound, detectado por Defender.
- Intento de borrado de logs que deja rastro en el canal de cortafuegos.

## Lecciones

- Cinco canales cruzados cuentan una historia; uno solo, no.
- Los `EventID` numéricos del cortafuegos (dirección, acción, protocolo) hay que traducirlos, no adivinarlos.
- Mitigación: reenviar logs a un servidor central (WEF/SIEM) para que el borrado local no destruya la evidencia, y alertar de `4719` y `104`.
