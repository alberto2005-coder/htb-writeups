---
sherlock: RogueOne
domain: DFIR / Memoria
difficulty: Easy
platform: Hack The Box
evidence: Volcado de memoria de un puesto de Forela
tools: [Volatility 3, windows.netscan, windows.pstree, strings]
state: Retired
tags: [dfir, memoria, volatility3, c2, windows]
---

# RogueOne — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El SIEM dispara varias alertas en menos de un minuto señalando posible **C2** desde el puesto de Simon Stark (Forela). No hay procesos sospechosos visibles en el Administrador de tareas, así que el SOC aísla la máquina y entrega un volcado de memoria para confirmar el canal y reconstruir la línea temporal.

## Evidencias

- Un único fichero: `20230810.mem`, volcado de memoria de Windows.

## Investigación

### 1. Procesos y árbol

```bash
vol -f 20230810.mem windows.pslist
vol -f 20230810.mem windows.pstree
```

`pslist` da PID, PPID y hora de creación. Un `svchost.exe` **fuera de `C:\Windows\System32`** —por ejemplo bajo `Downloads`— es el hallazgo: el nombre es legítimo, la ruta no.

### 2. Conexiones

Es el plugin que resuelve el caso:

```bash
vol -f 20230810.mem windows.netscan | grep <PID>
```

Devuelve una conexión `ESTABLISHED` desde ese PID a una IP externa en el puerto **8888**, establecida **en el mismo segundo** en que se creó el proceso: firma de *connect-on-start*.

### 3. Linaje

```bash
vol -f 20230810.mem windows.pstree | grep -A3 <PID>
```

El árbol muestra `explorer.exe → svchost.exe (falso) → cmd.exe → conhost.exe`: el implante lanza una shell, la firma de un canal de comandos interactivo.

### 4. Línea de comandos y huella

```bash
vol -f 20230810.mem windows.cmdline --pid <PID>
```

Con la ruta y el SHA-256/MD5 del ejecutable (volcado con `windows.dumpfiles` o `windows.memmap`) se busca el hash en VirusTotal; el informe da familia y etiquetas. La creación del proceso más el primer paquete del canal dan la hora de inicio del C2.

## Conclusiones

- C2 confirmado por memoria: proceso con nombre legítimo, ruta de usuario escribible y conexión saliente `ESTABLISHED`.
- El implante se creó y conectó en el mismo segundo y lanzó `cmd.exe`: ejecución de comandos remota.
- La evidencia es de endpoint, no de red: el volcado demuestra el canal aunque el EDR no viera nada raro.

## Lecciones

- En memoria, la ruta del binario pesa más que el nombre: `svchost.exe` en `Downloads` es malware.
- `netscan` + `pstree` + `pslist` responden «quién, a dónde y desde cuándo» sin desensamblar nada.
- *Connect-on-start* (proceso creado y conexión en el mismo timestamp) es un indicador de beaconing.
- El hash del ejecutable es lo que convierte el hallazgo en inteligencia compartible.
