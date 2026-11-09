---
sherlock: MangoBleed
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, triage, kape, timeline, persistence]
---

# MangoBleed — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Una empresa de logística detecta conexiones salientes raras en una estación de trabajo. Se entrega una **imagen de triaje** (artefactos volátiles y de disco) y hay que averiguar cómo entró el atacante, qué dejó instalado y qué se llevó.

## Evidencias

- Triaje tipo KAPE: `$MFT`, `UsnJrnl`, registro, `Prefetch`, `Amcache`, logs de eventos.
- Directorio de usuario con descargas y documentos recientes.
- Opcional: volcado de memoria.

## Investigación

### 1. Orden de trabajo

Empieza por lo que da contexto temporal y termina en el detalle:

```text
ejecución  -> Prefetch, Amcache, UserAssist, SRUM
persistencia -> Run keys, tareas programadas, servicios, Startup
acceso a ficheros -> LNK, JumpLists, RecentDocs
red -> logs de firewall/proxy, DNS cache
```

`PECmd` sobre `Prefetch` da primera ejecución, número de ejecuciones y ruta del binario; `AmcacheParser` añade hashes y metadatos del ejecutable.

### 2. Construir la línea de tiempo

```bash
log2timeline.py --storage-file mango.plaso triage/
psort.py -o l2tcsv mango.plaso "date > '2026-01-01'" > timeline.csv
```

La clave está en el orden: descarga del archivo comprimido → ejecución del instalador → creación de servicio o tarea → primeras conexiones. Cualquier salto en esa secuencia (por ejemplo, ejecución sin descarga visible) apunta a un segundo vector.

### 3. Persistencia

```bash
regipy-dump -o out/ NTUSER.DAT
grep -i "run" out/*.json | head
```

Se revisan `Run`/`RunOnce` (HKCU y HKLM), tareas programadas (`Windows\System32\Tasks`) y servicios nuevos. Un binario en `%APPDATA%` o `%LOCALAPPDATA%\Temp` referenciado desde ahí es el implante.

### 4. Exfiltración

Con la herramienta identificada se busca su rastro: directorios de staging (`.zip`, `.rar` con fechas del incidente), historial del navegador y conexiones a un dominio de transferencia. El volumen en `SRUM`/firewall ayuda a responder «cuánto salió».

## Conclusiones

- Acceso por descarga y ejecución de un instalador troyanizado desde el navegador.
- Persistencia en el perfil del usuario, sin privilegios de administrador.
- Datos empaquetados y enviados a un servicio de almacenamiento externo.

## Lecciones

- El triaje permite responder casi todo sin memoria: ejecución, persistencia y acceso a ficheros están en disco.
- `Prefetch` + `Amcache` + `UserAssist` son el trío para «qué se ejecutó y cuándo».
- La persistencia en el perfil del usuario evade controles que solo miran servicios del sistema.
