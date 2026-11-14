---
sherlock: APTNightmare-2
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, memory, linux, volatility3, dwarf2json, rootkit, apt]
---

# APTNightmare-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un servidor Linux corporativo se reinició de forma anómala y el equipo de respuesta capturó la memoria antes de apagarlo. Se entrega el volcado, el `System.map` y un perfil genérico. Hay sospechas de un actor con acceso root y persistencia oculta.

## Evidencias

- `memdump.mem` (volcado de memoria).
- `System.map` del kernel en ejecución.
- `profile.json` o descripción del perfil genérico.
- No se entrega imagen de disco.

```bash
ls -lh memdump.mem System.map
strings -a memdump.mem | grep -m3 'Linux version'
```

## Investigación

### 1. Preparación de símbolos

Volatility 3 no reconoce el kernel por defecto. Se obtiene la versión exacta del banner y se construye un ISF (Intermediate Symbol Format) con `dwarf2json`, usando `System.map` y, si está disponible, el `vmlinux` correspondiente.

```bash
dwarf2json linux --system-map System.map --elf vmlinux > linux-<VERSION>.json
mkdir -p volatility3/volatility3/symbols/linux
cp linux-<VERSION>.json volatility3/volatility3/symbols/linux/
```

Si no hay `vmlinux`, se puede usar un kernel del mismo build y verificar que los offsets coinciden. Un perfil incorrecto produce resultados vacíos o erróneos.

### 2. Procesos y línea de comandos

Se listan procesos y se reconstruye el árbol. Un `bash` con PPID de un servicio y una sesión interactiva es sospechoso. `linux_bash` recupera el historial de la sesión.

```bash
vol -f memdump.mem linux_pslist
vol -f memdump.mem linux_pstree
vol -f memdump.mem linux_bash
```

En el historial aparece `sudo su`, seguido de comandos de reconocimiento y de un proceso que abre una shell reversa. El binario `sudo` legítimo se usa para elevar privilegios, no hay exploit.

### 3. Red y persistencia

`linux_netscan` muestra una conexión saliente desde un proceso que no debería tener red. Se revisan módulos y tareas programadas para localizar la persistencia.

```bash
vol -f memdump.mem linux_netscan
vol -f memdump.mem linux_lsmod
vol -f memdump.mem linux_enumerate_files | grep -iE 'cron|systemd|rc.local'
```

El actor dejó un servicio o tarea que vuelve a lanzar el implant tras el reinicio. Un módulo cargado fuera de la ruta estándar sugiere un rootkit.

### 4. Correlación y línea temporal

Se ordenan los eventos por hora de inicio de proceso y por conexiones. La secuencia es: acceso inicial por credenciales, `sudo su`, descarga de herramientas, shell reversa, persistencia y limpieza de logs.

```text
login → sudo su → reconocimiento → descarga → shell reversa → persistencia → borrado de logs
```

## Conclusiones

- El atacante obtuvo root con credenciales válidas, no con una vulnerabilidad del kernel.
- La memoria permite recuperar el historial y la conexión C2.
- La persistencia sobrevive al reinicio mediante un servicio o tarea.
- El rootkit oculta parte de la actividad, pero no toda la telemetría.

## Lecciones

- Sin símbolos correctos, Volatility 3 no es fiable.
- `linux_bash` y `linux_netscan` son puntos de partida rápidos en memoria Linux.
- La ausencia de disco no impide reconstruir la intrusión.
- Un rootkit exige comparar con una línea base externa.

## Referencias

- <https://www.hackthebox.com/sherlocks/APTNightmare-2>
- <https://github.com/volatilityfoundation/volatility3>
- <https://github.com/volatilityfoundation/dwarf2json>
- <https://attack.mitre.org/techniques/T1014/>
