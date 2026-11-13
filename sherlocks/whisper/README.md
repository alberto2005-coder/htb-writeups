---
sherlock: Whisper
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, registry, mft, mimikatz, shellbags, sam]
---

# Whisper — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un endpoint Windows muestra signos de acceso no autorizado y robo de credenciales. Se entrega una colección forense para identificar la ejecución de herramientas, los archivos descargados y los artefactos de navegación.

## Evidencias

- Hives `SYSTEM`, `SOFTWARE`, `SAM` y `NTUSER.DAT`.
- `$MFT` y `$UsnJrnl`.
- Prefetch.
- Historial y descargas de Microsoft Edge.
- ShellBags y archivos LNK.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Inventario y triaje

Se identifican el perfil del usuario, la zona horaria y el intervalo de interés. Los hives se cargan en herramientas de análisis y se genera un timeline con MFT y USN.

```bash
RegistryExplorer.exe
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
```

### 2. Ejecución y descarga

Prefetch confirma la ejecución de `mimikatz` y de utilidades de acceso remoto. El historial de Edge y la carpeta `Downloads` muestran el origen de los archivos.

- Nombre y ruta del ejecutable.
- Primer y último acceso.
- URL de descarga y nombre original.
- Relación temporal con la creación de archivos en `Temp`.

### 3. Acceso a credenciales y navegación

La ejecución de Mimikatz se correlaciona con el acceso al proceso `lsass`. Los ShellBags y LNK revelan carpetas y archivos abiertos, incluso si fueron borrados. El hive `SAM` se revisa para cuentas locales y cambios recientes.

## Conclusiones

- Herramienta ejecutada y usuario que la lanzó.
- Archivos descargados y su procedencia.
- Evidencia de acceso a credenciales.
- IOCs: rutas, nombres y hashes, redactados.

## Lecciones

- Prefetch y USN se complementan: uno confirma ejecución, el otro el orden de los archivos.
- Los ShellBags sobreviven al borrado del contenido.
- El acceso a `lsass` debe correlacionarse con permisos y con el binario utilizado.

## Referencias

- <https://www.hackthebox.com/sherlocks/Whisper>
- <https://attack.mitre.org/techniques/T1003/001/>
- <https://ericzimmerman.github.io/>
- <https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess>
