---
sherlock: OpTinselTrace-3
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, memory, volatility3, powershell, defender, procdump]
---

# OpTinselTrace-3 — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

El equipo de seguridad captura un volcado de memoria de una estación TinkerTech (`santaclaus.bin`). La cadena sigue a OpTinselTrace-2: el atacante usó el acceso a AWS para distribuir un archivo a un usuario interno. Hay que identificar el fichero entregado, el script ofuscado, el binario final y la exclusión de Defender.

## Evidencias

- `santaclaus.bin`, volcado de memoria Windows.
- Perfil de Volatility 3 para Windows.
- Ficheros y EVTX recuperables del volcado.
- Indicadores de PowerShell y Defender.

```bash
python3 vol.py -f santaclaus.bin windows.info
python3 vol.py -f santaclaus.bin windows.filescan > files.txt
```

## Investigación

### 1. Inventario y triaje

Se busca el perfil del usuario y los ficheros recientes:

```bash
grep -i 'santaclaus' files.txt | head -40
python3 vol.py -f santaclaus.bin windows.filescan | grep -iE 'present|\.zip|\.lnk|\.exe'
```

El volcado conserva un ZIP y un acceso directo (`click_for_present.lnk`), que apuntan al señuelo.

### 2. Línea temporal

- Descarga del ZIP y creación del LNK.
- Ejecución del LNK y del script de PowerShell.
- Ofuscación por concatenación y `GRINCH`/`WrapPresent`.
- Descarga de `present.exe` y ejecución.
- Exclusión de Defender y volcado con `procdump`.

```bash
python3 vol.py -f santaclaus.bin windows.dumpfiles --virtaddr <ADDR>
python3 vol.py -f santaclaus.bin windows.filescan | grep -i evtx
```

### 3. Artefacto clave

El LNK ejecuta un script que reconstruye cadenas y descarga el siguiente stage. `present.exe` contiene la IP/puerto del C2; `strings` puede dar la IP y IDA/Ghidra el puerto. Los EVTX de PowerShell muestran `Add-MpPreference` con una exclusión de carpeta y la ejecución de `PresentForNaughtyChild.exe`.

```text
ZIP -> LNK -> PowerShell ofuscado -> present.exe -> exclusión Defender -> procdump
```

## Conclusiones

- El atacante entregó un ZIP con un LNK y un script ofuscado.
- El script descargó y ejecutó un binario con C2.
- Se añadió una exclusión de Defender para evitar detección.
- Los IOCs son el nombre/hash del ZIP, LNK, script, EXE, IP/puerto y la ruta excluida.

## Lecciones

- Los LNK dentro de ZIP son un vector clásico de ejecución.
- La ofuscación por concatenación se revierte con CyberChef/PSDecode.
- La memoria conserva scripts y binarios que el disco ya no tiene.
- `Add-MpPreference` es una técnica de evasión detectable.

## Referencias

- <https://mwalkowski.com/post/sherlock-optinseltrace-3>
- <https://volatility3.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1562/001/>
