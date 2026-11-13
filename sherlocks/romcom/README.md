---
sherlock: RomCom
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, cve-2025-8088, mft, usn-journal, usb]
---

# RomCom — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Se investiga un equipo Windows donde un archivo comprimido aparentemente inofensivo desencadenó ejecución y persistencia. Se pide reconstruir la extracción, la ejecución y el momento exacto de los hechos.

## Evidencias

- Imagen forense del volumen del sistema.
- `$MFT` y `$UsnJrnl`.
- Prefetch y artefactos de ejecución.
- Registros de dispositivos USB.
- Copia del archivo comprimido y del acceso directo utilizado.

```bash
sha256sum <EVIDENCE>.zip
```

## Investigación

### 1. Inventario y triaje

Se documenta la zona horaria del equipo y se genera un timeline con MFT, USN y prefetch. Las fechas de creación, modificación y acceso se tratan como fuentes distintas.

```bash
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
PECmd.exe -d C:\Windows\Prefetch --csv out --csvf prefetch.csv
```

### 2. Extracción y ejecución

Se busca el nombre del archivo comprimido y la ruta de extracción. CVE-2025-8088 abusa de la ruta de un archivo dentro de un archivo comprimido para escribir fuera del destino esperado. El resultado suele ser un acceso directo o ejecutable colocado en una ruta de inicio.

- Fecha de creación del archivo extraído.
- Ruta real frente a ruta mostrada por el compresor.
- Primer acceso y ejecución del binario o LNK.
- Relación con el prefetch y con el USN.

### 3. Persistencia y propagación

Se revisan `Startup`, `Run`, tareas programadas y el registro de dispositivos USB. Un acceso directo en una unidad extraíble puede ejecutarse en otro equipo y explicar la propagación.

## Conclusiones

- Archivo comprimido y ruta de extracción.
- Acceso directo o binario creado fuera del directorio esperado.
- Ejecución confirmada por prefetch y USN.
- IOCs: nombres, rutas y hashes, redactados.

## Lecciones

- La ruta visible en un compresor no es la ruta real en disco.
- `$UsnJrnl` aporta el orden de creación y renombrado que el MFT no muestra por sí solo.
- Los accesos directos en unidades USB son vectores de propagación.

## Referencias

- <https://www.hackthebox.com/sherlocks/RomCom>
- <https://nvd.nist.gov/vuln/detail/CVE-2025-8088>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://ericzimmerman.github.io/>
