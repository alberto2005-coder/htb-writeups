---
sherlock: Detroit becomes Human
domain: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, msi, browser-extension, mft, prefetch]
---

# Detroit becomes Human — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

Un sysadmin de Forela descarga una supuesta herramienta de IA desde un anuncio en redes sociales. Tras instalarla, no encuentra la aplicación y sospecha. Se entrega una copia parcial del disco del equipo con Prefetch, EVTX, perfiles de usuario y `$MFT`; hay que reconstruir la instalación, el script que se ejecuta y la extensión del navegador que actúa como persistencia.

## Evidencias

- Copia de `C:` con ~492 archivos de interés.
- `Prefetch`, `Amcache`, EVTX y `$MFT`.
- Perfil del usuario con `Downloads`, `AppData` y navegadores.
- Historial de Edge/Chrome y base de datos de extensiones.

```bash
sha256sum detroit.zip
unzip -l detroit.zip | head -40
```

## Investigación

### 1. Inventario y triaje

Se empieza por el navegador porque el anuncio y la descarga son el origen:

```text
C/Users/<USER>/AppData/Local/Microsoft/Edge/User Data/Default/History
C/Users/<USER>/AppData/Local/Google/Chrome/User Data/Default/History
```

```bash
sqlite3 History "select url, title, last_visit_time from urls order by last_visit_time desc limit 30;"
sqlite3 History "select tab_url, target_path, start_time from downloads;"
```

El historial muestra el post patrocinado y la descarga del instalador MSI.

### 2. Línea temporal

- Visita al anuncio y descarga del MSI.
- Instalación: evento 11707 (MSI) y creación de servicios/ficheros.
- Ejecución de `ru.ps1` desde una ruta de Google.
- Creación de una extensión de Chrome y su `content.js`.
- Borrado del RAR de instalación.

```bash
chainsaw search -t 'Event.System.EventID: =11707' --skip-errors C/Windows/System32
MFTECmd.exe -f '$MFT' --csv mft.csv
```

### 3. Artefacto clave

El MSI instala una extensión de Chrome en una carpeta que imita a Google. `content.js` comprueba `localStorage` y envía un mensaje a `background.js` para ejecutar la función principal. La extensión sobrevive al cierre del navegador y es la persistencia.

```text
Anuncio -> MSI -> ru.ps1 -> extensión Chrome -> background.js/content.js
```

El MFT confirma la creación del script y del RAR, y el borrado del instalador. El informe de Any.run del MSI permite contrastar el nombre original y el comportamiento.

## Conclusiones

- El usuario instaló un MSI falso desde un anuncio.
- El instalador desplegó un script de PowerShell y una extensión de Chrome.
- La extensión es la persistencia y el canal de ejecución.
- Los IOCs son el nombre/hash del MSI, la ruta de `ru.ps1`, la extensión y el RAR.

## Lecciones

- Los anuncios patrocinados son un vector de distribución de malware.
- Un MSI deja eventos 11707 y cambios en `Program Files`.
- Las extensiones de Chrome son persisted user-level y fáciles de pasar por alto.
- El MFT reconstruye la instalación aunque el instalador se borre.

## Referencias

- <https://mwalkowski.com/post/sherlock-detroit-becomes-human>
- <https://learn.microsoft.com/en-us/windows/win32/msi/event-logging>
- <https://attack.mitre.org/techniques/T1176/>
