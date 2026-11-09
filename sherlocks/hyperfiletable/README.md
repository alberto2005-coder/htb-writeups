---
sherlock: Hyperfiletable
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Un único registro de la MFT de un equipo con phishing
tools: [MFTECmd, MFTExplorer, Timeline Explorer, hexdump]
---

# Hyperfiletable — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un empleado nuevo de Forela descarga su documentación de bienvenida, pero alguien le coló un adjunto malicioso por phishing. Del equipo sólo se pudo recuperar **el registro de la MFT**: con eso hay que triar qué pasó.

## Evidencia

- Un `$MFT` (y, según el caso, su CSV ya parseado).

## Método

1. **Parsear**: `MFTECmd` convierte la MFT en CSV.

```bash
MFTECmd.exe -f '$MFT' --csv . --csvf mft.csv
```

2. **Usuario**: el perfil con actividad es el único usuario real del sistema; sus rutas (`C:\Users\<usuario>\...`) lo confirman.

3. **Adjunto**: buscar extensiones ejecutables o de scripting descargadas por el navegador — un `.hta`, `.js`, `.lnk` o `.zip` en `Downloads`.

4. **Origen**: la **Zone.Identifier** es un flujo alternativo (`file:Zone.Identifier:$DATA`). `ZoneId=3` significa "descargado de Internet"; junto a ella aparece `HostUrl` con la URL de descarga.

5. **Cronología**: `Creation`/`Modified`/`MFTModified` de la descarga, del adjunto y de los procesos/ficheros derivados. Con sólo MFT, los tiempos son la única línea temporal.

## Qué enseña

- La MFT es un índice de todo lo que existió en el volumen: nombres, tamaños, marcas de tiempo y atributos.
- Un `ZoneId=3` prueba que el fichero vino de Internet, sin necesidad del historial del navegador.
- `HostUrl` guarda la URL exacta de la descarga: IOC directo.
- El tamaño del registro (`AllocatedSize`/`RealSize`) delata huecos y borrados.

## Tropiezos

- **Sólo MFT**: no hay contenido de ficheros; no se puede hashear el adjunto.
- **Zona horaria**: exportar en UTC y normalizar antes de cruzar con otros artefactos.
- **Registros sobrescritos**: en NTFS un registro reutilizado pierde los datos anteriores.
