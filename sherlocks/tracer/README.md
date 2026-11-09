---
sherlock: Tracer
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, psexec, prefetch, mft, lateral-movement, windows]
---

# Tracer — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El SOC recibió varias alertas por **PsExec** en un puesto de trabajo y las escaló a nivel 2. Se entrega el *triage* de un único endpoint: hay que demostrar si el atacante se movió lateralmente, cuántas veces ejecutó PsExec y desde qué host vino.

## Evidencias

- Logs operativos de `PSEXESVC` (canal de servicio).
- `Prefetch` del sistema.
- Tabla MFT / artefactos de sistema de ficheros.

## Investigación

### 1. Del artefacto al ejecutable

```bash
PECmd.exe -d C:/triage/Prefetch -o out/
```

En Timeline Explorer se filtra `psexec` y se cuentan las ejecuciones y sus marcas de tiempo. El binario de servicio que PsExec deja caer es **`psexesvc.exe`**: aparece en `Prefetch`, en MFT y en el log del servicio como ejecutable instalado (evento `7045`).

```cmd
wevtutil qe System /q:"*[System[EventID=7045]]" /f:text
```

### 2. Contar las ejecuciones

Cada sesión deja una entrada en el canal operativo del servicio. Contar los arranques (`PSEXESVC` iniciado) da el número de veces; comprobar que coinciden con las entradas de `Prefetch` y con los ficheros creados evita contar reconexiones como ejecuciones nuevas.

### 3. El rastro del nombre de origen

PsExec nombra sus artefactos con el host de origen:

```text
PSEXEC-<HOST>-<PID>.key
\PSEXESVC-<HOST>-<PID>-stderr
\PSEXESVC-<HOST>-<PID>-stdin
```

Buscando `*.key` en el triage (o la cadena del pipe en el log) sale el nombre del equipo desde el que se lanzó la herramienta. Se confirma con la línea de comandos registrada en el evento de creación del servicio, donde aparece la ruta UNC de origen.

### 4. Cronología

Ordenar: instalación del servicio → creación del `.key` → pipe → ejecución del comando. Las diferencias de uno o dos segundos son normales; si hay minutos, probablemente sean sesiones distintas.

```bash
MFTECmd.exe -f C:/triage/$MFT -o out/
```

## Conclusiones

- Herramienta: PsExec, ejecutada varias veces sobre el mismo host.
- Binario de servicio: `psexesvc.exe`, con su `.key` y pipes asociados.
- Origen: host identificado por el nombre de los artefactos y por la línea de comandos del `7045`.

## Lecciones

- PsExec deja tres huellas independientes (servicio, `.key`, pipe): coinciden o la atribución es débil.
- Prefetch y MFT dan el «cuándo»; el log del servicio da el «desde dónde».
- Mitigación: monitorizar `7045` con binarios en `ADMIN$`, bloquear SMB entre estaciones y alertar de `psexesvc.exe`.
