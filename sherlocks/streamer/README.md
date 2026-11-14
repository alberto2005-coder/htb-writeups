---
sherlock: Streamer
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, windows, webcache, amcache, shellbags, timeline]
---

# Streamer — Hack The Box (Sherlock)

[🐬 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un equipo de streaming fue comprometido y se borraron archivos. Se entrega una imagen forense con pocos eventos de ejecución; hay que reconstruir la actividad desde artefactos menos evidentes.

## Evidencias

- `WebCacheV01.dat`, `Amcache.hve` y `UsrClass.dat`.
- `$MFT`, `$J` y `Windows.edb`.
- Historial de navegación y descargas.

```bash
sha256sum evidence/*
find evidence -iname 'WebCacheV01.dat' -o -iname 'Amcache.hve'
```

## Investigación

### 1. Navegación y descargas

`WECmd`/`ESEDatabaseView` leen `WebCacheV01.dat`. Se extraen URLs, nombres de archivo y timestamps; las descargas se cruzan con la MFT.

```bash
python3 -m pip install --user pyscca
```

### 2. Ejecución y carpetas

`Amcache` aporta primeros avistamientos y hashes. `SBECmd` muestra carpetas abiertas, incluidas las de la herramienta usada para borrar. La combinación compensa la falta de prefetch.

### 3. Reconstrucción

Se ordenan los eventos y se buscan huecos: un archivo borrado deja rastros en USN y MFT. La secuencia explica qué se descargó, ejecutó y eliminó.

## Conclusiones

- La navegación revela el origen del payload.
- Amcache y shellbags cubren la ausencia de prefetch.
- El USN muestra borrados y renombrados.
- La timeline es la conclusión, no un subproducto.

## Lecciones

- Los artefactos "secundarios" pueden ser la evidencia principal.
- Borrar un archivo no borra todos sus rastros.
- Cada fuente tiene una resolución temporal distinta.
- La correlación es obligatoria en DFIR.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman>
- <https://attack.mitre.org/techniques/T1070/004/>
