---
topic: Shellbags en Windows
tags: [forensics, windows, shellbags, usrclass, registry]
---

# Shellbags en Windows

[🐬 English](shellbags.en.md) | **Español**

## Concepto

Las shellbags registran carpetas que el usuario abrió en el Explorador, incluidas rutas de red y unidades extraíbles. Se almacenan en `UsrClass.dat` y `NTUSER.DAT` y sobreviven a la eliminación de la carpeta.

## Cuándo aplica

- Reconstruir navegación por directorios.
- Confirmar acceso a una unidad USB o a un recurso UNC.
- Correlacionar con USBSTOR, MFT y LNK.

## Procedimiento

1. Copiar `UsrClass.dat` y `NTUSER.DAT` de cada perfil.
2. Procesarlos con `SBECmd`.
3. Filtrar por ruta, volumen y fecha.
4. Cruzar con USB y MFT.
5. Documentar la ruta y el timestamp.

```bash
SBECmd.exe -d evidence/Users --csv shellbags
```

## Variantes

- BagMRU/Bags en `NTUSER.DAT`.
- Rutas de red y dispositivos MTP.
- Shellbags por aplicación (Office, exploradores).

## Limitaciones

- No prueba que un archivo se copiara.
- Las fechas pueden reflejar la primera o última visita.
- Perfiles sin `UsrClass.dat` no aportan.

## Mitigación

- Limpiar historial al desmontar medios.
- Restringir acceso a recursos de red.
- Auditar el uso de dispositivos extraíbles.

## Detección

- Rutas a unidades no autorizadas.
- Accesos a `\host\share` desde estaciones.
- Correlación con eventos USB.

## Referencias

- <https://github.com/EricZimmerman/SBECmd>
- <https://attack.mitre.org/techniques/T1059/>
- <https://www.hackthebox.com/sherlocks>
