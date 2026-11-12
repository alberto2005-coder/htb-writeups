---
sherlock: Unsupervised
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, registry, usb, jumplists, thumbcache]
---

# Unsupervised — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un empleado sospechoso ha estado copiando información fuera de la empresa. Se entrega un triaje de su puesto Windows: colmenas de registro, listas de salto, caché de miniaturas y artefactos de dispositivos. Hay que determinar qué unidad USB se conectó, cuándo, qué archivos se abrieron o copiaron y qué evidencia visual queda de ellos.

## Evidencias

- `C:\Users\<USER>\NTUSER.DAT` y `UsrClass.dat`.
- `C:\Windows\System32\config\SYSTEM` (para `USBSTOR` y `MountedDevices`).
- `AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\*.automaticDestinations-ms`.
- `AppData\Local\Microsoft\Windows\Explorer\thumbcache_*.db`.
- `AppData\Local\Microsoft\Windows\Explorer\` y `ShellBags`.
- `C:\Windows\INF\setupapi.dev.log`.

```bash
sha256sum NTUSER.DAT UsrClass.dat SYSTEM setupapi.dev.log
```

Se trabaja sobre copias. Las colmenas se cargan en Registry Explorer o con `reg.py`; no se montan en el registro del equipo de análisis.

## Investigación

### 1. Inventario y triaje

Se identifica el perfil y se revisan los artefactos de dispositivo. La primera pregunta es si hubo conexión USB y qué identificador tiene.

```bash
grep -a -i "USBSTOR\|RemovableMedia\|Disk&Ven" SYSTEM | head
```

En `SYSTEM\CurrentControlSet\Enum\USBSTOR` aparecen fabricante, modelo y número de serie. `MountedDevices` relaciona la unidad montada (`\DosDevices\E:`) con el volumen. `setupapi.dev.log` conserva la hora de primera instalación del dispositivo.

### 2. Línea temporal

Se cruzan:

- Primera conexión del USB (`setupapi.dev.log` y `USBSTOR`).
- Entradas `MountPoints2` en `NTUSER.DAT` con el GUID del volumen.
- Apertura de archivos en listas de salto y `RecentDocs`.
- Actividad de ShellBags por carpeta.
- Miniaturas generadas al visualizar imágenes o documentos.

Las listas de salto `AutomaticDestinations` se parsean con JLECmd; los ShellBags con ShellBags Explorer; la thumbcache con ThumbCache Viewer. Hay que normalizar las horas (algunos artefactos guardan UTC, otros hora local) y comprobar la zona del sistema.

### 3. Artefacto clave

El artefacto que cierra el caso es la combinación de tres piezas:

1. El número de serie del USB en `USBSTOR`.
2. El GUID de volumen en `MountPoints2`.
3. Una entrada de lista de salto o miniatura que apunta al archivo sensible.

La lista de salto demuestra que el usuario abrió el archivo desde una ruta de unidad extraíble; la miniatura demuestra que el contenido se mostró en el equipo. La correlación con `setupapi.dev.log` sitúa la conexión en el tiempo.

```text
USBSTOR\Disk&Ven_<VENDOR>&Prod_<PRODUCT>&Rev_<REV>
<VOLUME_GUID> -> \??\Volume{...}\
```

## Conclusiones

- Se conectó una unidad USB identificable por su número de serie.
- El usuario abrió o copió archivos desde esa unidad en una ventana temporal concreta.
- Las listas de salto y la caché de miniaturas conservan evidencia del contenido, aunque el archivo ya no esté.
- Los IOCs son el serial del dispositivo, el GUID de volumen y las rutas de los archivos.

## Lecciones

- `USBSTOR` prueba la conexión; no prueba por sí solo que se copiaran datos.
- Las listas de salto y los ShellBags aportan el “quién abrió qué”.
- La thumbcache puede conservar una imagen del documento incluso si el original se borró.
- La correlación de tres artefactos independientes es más fuerte que cualquier respuesta aislada.
