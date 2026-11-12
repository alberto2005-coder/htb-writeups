---
topic: Caché de mapas de bits RDP
tags: [forensics, windows, rdp, bitmap-cache, bmc-tools]
---

# Caché de mapas de bits RDP

[🇬🇧 English](rdp-bitmap-cache.en.md) | **Español**

## Concepto

El cliente RDP guarda teselas de la pantalla remota para acelerar el dibujado. Esos ficheros (`Cache*.bin`, `bcache*.bmc`) sobreviven al cierre de la sesión y pueden contener texto, documentos e imágenes que el usuario vio. `bmc-tools` extrae las teselas y permite reconstruir la pantalla.

## Cuándo aplica

- Hay un perfil de usuario Windows con caché RDP.
- Se investiga una sesión remota o un insider.
- Se necesita recuperar contenido visual que no está en el historial.
- El equipo no se ha limpiado después de la sesión.

## Requisitos y condiciones

1. Acceso a los ficheros de caché del perfil.
2. `bmc-tools` y un visor de imágenes.
3. Tiempo para ordenar teselas si el collage no respeta la posición.
4. Copia forense; no modificar los originales.

## Procedimiento

Localizar la caché:

```text
C:\Users\<USER>\AppData\Local\Microsoft\Terminal Server Client\Cache\
C:\Users\<USER>\AppData\Local\Microsoft\Windows\INetCache\
```

Extraer teselas:

```bash
git clone https://github.com/ANSSI-FR/bmc-tools
python3 bmc-tools/bmc-tools.py -s . -d bitmaps
```

Convertir y revisar:

```bash
mkdir png
mogrify -format png bitmaps/*.bmp
```

La opción `-b` genera un collage; si el orden no es correcto, se ordenan manualmente las teselas con texto.

## Variantes

- **RdpCacheStitcher**: interfaz gráfica para ordenar teselas.
- **Múltiples sesiones**: `Cache0000.bin`, `Cache0001.bin`, etc.; hay que separar por sesión.
- **`bcache*.bmc`**: caché de mapas de bits del cliente; puede estar vacía.
- **Escritorios virtuales**: la caché puede contener varias pantallas.

## Limitaciones

- Las teselas no siempre conservan el orden original.
- La caché es parcial: solo lo que se dibujó.
- El contenido puede estar comprimido o cifrado por la versión de RDP.
- La calidad puede ser baja; el texto pequeño es difícil de leer.

## Mitigación

- Limpiar la caché RDP al cerrar sesiones sensibles.
- Aplicar políticas de retención y borrado seguro.
- Restringir el acceso al perfil y usar equipos gestionados.
- Evitar sesiones RDP a datos sensibles desde equipos compartidos.

## Detección

- Acceso anómalo a `Cache*.bin`/`bcache*.bmc`.
- Herramientas de extracción de caché en el endpoint.
- Sesiones RDP fuera de horario o desde hosts no habituales.
- Volumen inusual de ficheros en la carpeta de caché.

MITRE ATT&CK: T1005 (Data from Local System), T1078 (Valid Accounts).

## Referencias

- <https://github.com/ANSSI-FR/bmc-tools>
- <https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-features>
- <https://attack.mitre.org/techniques/T1005/>
