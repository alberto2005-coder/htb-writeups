---
sherlock: WhyFind
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, registry, mft, browser, virtual-machine]
---

# WhyFind — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un equipo Windows presenta actividad que el usuario no reconoce. Se entrega una salida de triage KAPE para reconstruir qué se ejecutó, qué se descargó y si se creó una máquina virtual para ocultar actividad.

## Evidencias

- Salida KAPE con hives `SYSTEM`, `SOFTWARE`, `NTUSER.DAT` y `UsrClass.dat`.
- `$MFT` y `$UsnJrnl` del volumen del sistema.
- Historial y descargas del navegador.
- Artefactos de virtualización y ejecución reciente.

```bash
sha256sum *.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Inventario y triaje

Se identifican el host, la zona horaria y el rango temporal. KAPE suele separar `C\` y `Registry`; conviene procesar ambos con un timeline común.

```bash
EvtxECmd.exe -d C:\Windows\System32\winevt\Logs --csv out --csvf security.csv
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
```

Los artefactos de ejecución se ordenan por fecha y se correlacionan con los eventos de red.

### 2. Línea temporal

- Creación y modificación de perfiles de usuario.
- Primer y último acceso a los archivos descargados.
- Ejecución de instaladores y binarios desde rutas de usuario.
- Aparición de dispositivos o discos virtuales.

La hora de `$MFT` y la de los EVTX pueden diferir; se documenta la fuente y la zona horaria.

### 3. Artefacto clave

El rastro de una máquina virtual en `NTUSER.DAT`, `UsrClass.dat` y los recientes del Explorador explica la actividad que el usuario no reconocía. Los nombres de los discos virtuales y las rutas de los instaladores permiten reconstruir el orden.

## Conclusiones

- Qué usuario inició la actividad y desde qué sesión.
- Qué software se instaló y qué archivos se abrieron.
- Qué artefactos demuestran la creación de la VM.
- IOCs: rutas, nombres de ejecutables y hashes, redactados.

## Lecciones

- KAPE no sustituye el análisis: hay que cruzar hives, MFT y navegador.
- Los artefactos de virtualización son fáciles de pasar por alto.
- Un timeline sin zona horaria documentada produce conclusiones falsas.

## Referencias

- <https://www.hackthebox.com/sherlocks/WhyFind>
- <https://ericzimmerman.github.io/>
- <https://attack.mitre.org/techniques/T1564/001/>
