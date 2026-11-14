---
sherlock: Baggage
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, shellbags, kape, usb]
---

# Baggage — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un empleado conecta dispositivos extraíbles y accede a carpetas fuera de su perfil. Se entrega una colección KAPE de un equipo Windows y se pide reconstruir qué carpetas y unidades visitó.

## Evidencias

- `UsrClass.dat` y `NTUSER.DAT` de cada perfil.
- `$MFT`, `$J` y registros de dispositivos USB.
- Salida de KAPE con la estructura de directorios.

```bash
sha256sum -c hashes.txt
tree -L 3 evidence | head -60
```

## Investigación

### 1. Inventario y alcance

Se identifican los perfiles y se separan los artefactos de usuario de los del sistema. Se anotan las rutas y los timestamps antes de ejecutar herramientas.

```bash
find evidence -iname 'UsrClass.dat' -o -iname 'NTUSER.DAT'
```

### 2. Shellbags

`SBECmd` procesa `UsrClass.dat` y muestra carpetas abiertas, incluidas rutas de red y unidades extraíbles. Se correlacionan con `USBSTOR` y con la `$MFT` para distinguir acceso real de una simple entrada.

```bash
SBECmd.exe -d evidence/Users --csv shellbags
```

### 3. Línea temporal

Las fechas de shellbags se comparan con la conexión USB y con los archivos creados. La secuencia muestra qué carpeta se abrió primero y qué unidad se utilizó.

## Conclusiones

- Las shellbags demuestran navegación por carpetas, no solo presencia.
- La unidad extraíble se confirma con USBSTOR y la MFT.
- La línea temporal permite ordenar acceso y copia.

## Lecciones

- `UsrClass.dat` conserva rutas que el usuario vio.
- KAPE acelera la recolección, pero hay que validar los artefactos.
- Una conclusión necesita al menos dos fuentes.
- Los dispositivos USB dejan rastro en varios registros.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/SBECmd>
- <https://attack.mitre.org/techniques/T1059/>
