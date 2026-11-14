---
topic: Alternate Data Streams (ADS)
tags: [windows, ntfs, ads, data-hiding, forensics, powershell]
---

# Alternate Data Streams (ADS)

[🌐 English](alternate-data-streams.en.md) | **Español**

## Concepto

NTFS permite asociar flujos de datos adicionales a un archivo mediante la sintaxis `archivo:flujo:$DATA`. El flujo principal no cambia de tamaño ni de contenido, por lo que se pueden ocultar contraseñas, binarios o notas en archivos aparentemente normales.

## Cuándo aplica

- Volúmenes NTFS en Windows.
- Archivos compartidos por SMB.
- Aplicaciones que guardan metadatos en flujos.
- Búsqueda de credenciales o payloads ocultos.

## Procedimiento

1. Listar flujos con `dir /r` o PowerShell.
2. Leer el contenido del flujo.
3. Comprobar si el flujo se ejecuta o se interpreta.
4. Extraer el dato para el análisis.
5. Documentar ruta, nombre y tamaño.

```powershell
Get-Item .\file.txt -Stream *
Get-Content .\file.txt -Stream Password
cmd /c dir /r
```

## Variantes

- Flujo `:Password:$DATA` con una contraseña.
- Flujo `:Zone.Identifier` con la procedencia de una descarga.
- Binario oculto en un flujo y ejecutado con `wmic` o `rundll32`.
- Flujos en directorios y en archivos de sistema.

## Limitaciones

- Requiere NTFS; FAT/exFAT no lo soporta.
- Copiar el archivo a otro sistema puede perder los flujos.
- Algunas herramientas no muestran ADS por defecto.
- Los backups y antivirus pueden inspeccionarlos.

## Mitigación y detección

- Monitorizar la creación de flujos y el acceso a `:*:$DATA`.
- Analizar los flujos en el triaje y en las descargas.
- Bloquear la ejecución desde rutas de usuario.
- Alertar de `dir /r`, `Get-Item -Stream` y procesos que leen flujos.

## Referencias

- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c54dec26-1551-4d3a-a0ea-4fa40f848eb3>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-item>
- <https://forensics.wiki/alternate_data_streams/>
