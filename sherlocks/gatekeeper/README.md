---
sherlock: GateKeeper
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, macos, unified-logs, gatekeeper, safari, cve-2022-22616]
---

# GateKeeper — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un Mac corporativo muestra actividad sospechosa después de que el usuario abriera un archivo descargado. Se entrega una colección de artefactos macOS para determinar cómo se saltó Gatekeeper, qué se ejecutó y cómo se escalaron privilegios.

## Evidencias

- Unified logs (`log show` o `logarchive`).
- Historial y descargas de Safari.
- Base de datos de cuarentena y metadatos de LaunchServices.
- Artefactos de ejecución, persistencia y cuentas.

```bash
log show --archive system.logarchive --start "2026-01-01" --end "2026-01-02" --style json > unified.json
```

## Investigación

### 1. Inventario y triaje

Se datan el equipo, la versión de macOS y la sesión del usuario. Se revisan descargas, volúmenes montados y aplicaciones ejecutadas desde rutas de usuario.

```bash
sqlite3 ~/Library/History.db "select datetime(v.visit_time + 978307200, 'unixepoch'), i.url from history_visits v join history_items i on v.history_item=i.id;"
```

### 2. Línea temporal

- Descarga del archivo y primer aviso de Gatekeeper.
- Apertura del paquete o del binario.
- Ejecución de procesos hijos y conexiones de red.
- Persistencia en LaunchAgents, LaunchDaemons o login items.
- Cambio de privilegios y acceso a datos del usuario.

La unified log usa hora local del sistema; se normaliza a UTC para comparar.

### 3. Artefacto clave

El evento de cuarentena y el registro de LaunchServices muestran que el archivo se ejecutó sin la validación esperada. La combinación con la versión vulnerable permite atribuir el bypass a CVE-2022-22616; después se observa una escalada local asociada a CVE-2019-8513.

```bash
xattr -l <DOWNLOAD>
sqlite3 ~/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2.db \
  "select datetime(LSQuarantineTimeStamp + 978307200,'unixepoch'), LSQuarantineDataURLString from LSQuarantineEvent;"
```

## Conclusiones

- Qué descarga inició la cadena y qué app la abrió.
- Cómo se evitó la comprobación de Gatekeeper.
- Qué procesos y persistencia quedaron.
- IOCs: URL, bundle, ruta y hash, redactados.

## Lecciones

- En macOS, la cuarentena y LaunchServices son tan importantes como los logs.
- Un bypass de Gatekeeper no siempre deja un evento explícito; hay que cruzar fuentes.
- La persistencia del usuario puede sobrevivir a la eliminación de la app.

## Referencias

- <https://www.hackthebox.com/sherlocks/GateKeeper>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-22616>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-8513>
- <https://attack.mitre.org/techniques/T1553/001/>
