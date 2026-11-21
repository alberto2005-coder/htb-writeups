---
topic: Windows — WerTrigger y carga de DLL privilegiada
tags: [windows, wertrigger, wer, dll, elevacion, proper]
---

# Windows — WerTrigger y carga de DLL privilegiada

[🌐 English](wertrigger-privesc.en.md) | **Español**

## Concepto

Windows Error Reporting (WER) se ejecuta con privilegios elevados cuando un proceso falla. WerTrigger es una herramienta que coloca un archivo y provoca un fallo para que WER cargue una DLL desde una ruta controlada. Si se dispone de escritura arbitraria en una ruta que WER revisa, se obtiene ejecución como SYSTEM. En Proper, la escritura arbitraria del servicio `Cleanup` se combinó con WerTrigger para cerrar la máquina.

## Cuándo aplica

- Hay escritura arbitraria como SYSTEM o en una ruta de búsqueda de DLL.
- WER está habilitado y se ejecuta con privilegios.
- Se puede provocar un crash de un proceso.
- La ruta de la DLL no está protegida.

## Procedimiento

1. Identificar una escritura arbitraria o una ruta de DLL.
2. Colocar la DLL maliciosa con el nombre esperado.
3. Provocar el fallo de WER.
4. Esperar a que WER cargue la DLL.
5. Comprobar la ejecución como SYSTEM.

## Comandos

```powershell
# El POC escribe phoneinfo.dll en System32 y provoca un fallo de WER
Copy-Item .\phoneinfo.dll C:\Windows\System32\phoneinfo.dll
```

```text
%LOCALAPPDATA%\Microsoft\Windows\WER\
C:\ProgramData\Microsoft\Windows\WER\
```

## Variantes

- Abusar de `RegisterWaitForInputIdle` o de un crash controlado.
- Combinar con un servicio que restaura archivos como SYSTEM.
- Usar una ruta de búsqueda de DLL de un proceso privilegiado.
- Aprovechar WER para cargar una DLL firmada o con nombre legítimo.
- Encadenar con `PrintNightmare` o `AlwaysInstallElevated`.

## Limitaciones

- WER puede estar deshabilitado por política.
- La ruta debe ser escribible y estar en la búsqueda de DLL.
- La DLL debe coincidir con la arquitectura del proceso.
- El crash debe ser reproducible.
- Las versiones modernas aplican mitigaciones de carga de DLL.

## Mitigación

- Deshabilitar WER en servidores o restringir su configuración.
- Proteger las rutas de WER y las carpetas de datos.
- Aplicar `SafeDllSearchMode` y rutas absolutas.
- Revisar servicios con escritura arbitraria.
- Monitorizar la creación de DLL en rutas de WER.

## Detección

- DLL nuevas en `%LOCALAPPDATA%\Microsoft\Windows\WER` o `C:\ProgramData`.
- Procesos `WerFault.exe` que cargan DLL de usuario.
- Crashes repetidos de un mismo proceso.
- Escrituras de DLL por servicios privilegiados.
- Carga de `phoneinfo.dll` por `WerFault.exe` o binarios desconocidos.

## Referencias

- [0xdf — Proper](https://0xdf.gitlab.io/2021/08/21/htb-proper.html)
- [GitHub — WerTrigger](https://github.com/sailay1996/WerTrigger)
- [Microsoft — Windows Error Reporting](https://learn.microsoft.com/en-us/windows/win32/wer/windows-error-reporting)
- [Ficha Proper](../../machines/windows/proper/README.md)
