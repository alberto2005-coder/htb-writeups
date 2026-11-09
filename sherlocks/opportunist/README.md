---
sherlock: Opportunist
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, memory, volatility, rat, browser-forensics, kill-chain]
---


# Opportunist — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un usuario de finanzas abre un archivo adjunto y, horas después, el equipo empieza a enviar tráfico a un VPS desconocido. Se entrega un **volcado de memoria**, un triaje del disco y la caché del navegador. Hay que reconstruir la cadena completa: entrega, ejecución, persistencia y exfiltración.

## Evidencias

- `memory.raw` (volcado completo).
- Triaje: registro, `Prefetch`, `Amcache`, `$MFT`.
- Caché y descargas del navegador.

## Investigación

### 1. Imagen del sistema desde memoria

```bash
vol -f memory.raw windows.info
vol -f memory.raw windows.pslist | tee pslist.txt
vol -f memory.raw windows.pstree
vol -f memory.raw windows.cmdline
```

Los procesos con nombre aleatorio en `%APPDATA%` o `%TEMP%`, sin firma y con línea de comandos vacía, son los candidatos. `pstree` revela el padre: un `explorer.exe` que lanza un binario desde `Downloads` es ejecución por doble clic del usuario.

### 2. Conexiones y C2

```bash
vol -f memory.raw windows.netscan | grep ESTABLISHED
vol -f memory.raw windows.dlllist --pid <PID>
```

`netscan` da IP/puerto remoto y proceso; con el PID se confirma que la conexión pertenece al implante y no al navegador. Las DLL cargadas desde rutas de usuario (`AppData`) en un proceso del sistema indican inyección.

### 3. Ejecución y persistencia en disco

```bash
PECmd.exe -d triage/Prefetch --csv out/
AmcacheParser.exe -f triage/Amcache.hve --csv out/
regipy-dump -o out/ triage/NTUSER.DAT
```

Se cruza la primera ejecución con la hora del correo/descarga. La persistencia típica de un RAT oportunista: `Run` en HKCU apuntando a `%APPDATA%\Roaming\<carpeta>\<binario>.exe`, o una tarea programada con nombre de actualización.

### 4. Actividad del usuario y exfiltración

```bash
python3 chrome_cache.py triage/Default/Cache
sqlite3 triage/Default/History "select url, last_visit_time from urls order by last_visit_time desc limit 20;"
```

La caché del navegador conserva el fichero descargado y su origen; el historial da la hora de la descarga. Con la ventana temporal se buscan archivos comprimidos creados después y se correlacionan con el tráfico de `netscan`.

## Conclusiones

- Entrega por descarga desde el navegador de un archivo que el usuario ejecutó manualmente.
- RAT con C2 a un VPS, persistencia en el perfil y capacidad de ejecutar comandos.
- Datos financieros empaquetados y enviados por el mismo canal.

## Lecciones

- La memoria responde «qué corría y con quién hablaba»; el disco responde «cómo llegó y cómo vuelve».
- El proceso padre es la prueba de si hubo exploit o error humano.
- Un RAT oportunista no necesita 0-day: adjunto + doble clic + `Run` key.
