---
sherlock: Hyperfiletable
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Un único registro de la MFT de un equipo con phishing
tools: [MFTECmd, MFTExplorer, Timeline Explorer, hexdump]
state: Retired
tags: [dfir, dfir-/-windows]
---


# Hyperfiletable — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un empleado nuevo de Forela descarga su documentación de bienvenida, pero alguien le coló un adjunto malicioso por phishing. Del equipo sólo se pudo recuperar **el registro de la MFT**: con eso hay que triar qué pasó.

## Evidencias

- Un `$MFT` comprimido con **bzip2** (se descomprime antes de parsear; el MD5 que pide el reto es el del `$MFT` descomprimido, no el del archivo).

## Investigación

1. **Parsear**: `MFTECmd` convierte la MFT en CSV.

```bash
MFTECmd.exe -f '$MFT' --csv . --csvf mft.csv
```

2. **Usuario**: el perfil con actividad es el único usuario real del sistema; sus rutas (`C:\Users\<usuario>\...`) lo confirman.

3. **Adjunto**: en este caso es un **`.hta`** descargado desde un enlace tipo Google Drive, junto a un PowerPoint legítimo que hace de señuelo. Buscar extensiones ejecutables o de scripting en `Downloads`.

4. **Origen**: la **Zone.Identifier** es un flujo alternativo (`file:Zone.Identifier:$DATA`). `ZoneId=3` significa "descargado de Internet"; junto a ella aparece `HostUrl` con la URL de descarga.

5. **Cronología**: `Creation`/`Modified`/`MFTModified` de la descarga, del adjunto y de los procesos/ficheros derivados. Con sólo MFT, los tiempos son la única línea temporal.

## Conclusiones

El nuevo empleado descargó un `.hta` malicioso desde un enlace externo y lo ejecutó: la MFT conserva la ruta, el `Zone.Identifier` con `ZoneId=3` y el `HostUrl` de la descarga, y la diferencia entre tamaño real y asignado delata el fichero y sus restos.

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- Un `ZoneId=3` prueba que el fichero vino de Internet, sin necesidad del historial del navegador.
- `HostUrl` guarda la URL exacta de la descarga: IOC directo.
- El tamaño del registro (`AllocatedSize`/`RealSize`) delata huecos y borrados.

## Tropiezos

- **Sólo MFT**: no hay contenido de ficheros; no se puede hashear el adjunto.
- **Zona horaria**: exportar en UTC y normalizar antes de cruzar con otros artefactos.
- **Registros sobrescritos**: en NTFS un registro reutilizado pierde los datos anteriores.
