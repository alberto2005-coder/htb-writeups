---
challenge: No Place To Hide
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, rdp, bitmap-cache, bmc-tools, image-reconstruction]
---

# No Place To Hide — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flag real.

## TL;DR

Se entregan los ficheros de caché de una sesión RDP (`Cache0000.bin` y `bcache24.bmc`). `bmc-tools` extrae más de mil teselas BMP; al convertirlas y unirlas se reconstruye la pantalla que el usuario vio, incluida la flag.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Ficheros de caché de mapas de bits de una sesión RDP.
- El contexto es un ataque de password spray y una sesión RDP sospechosa.

```bash
file Cache0000.bin bcache24.bmc
du -h Cache0000.bin bcache24.bmc
```

`bcache24.bmc` puede estar vacío; la evidencia útil está en `Cache0000.bin`.

## Reconocimiento

La caché RDP almacena teselas de la pantalla para acelerar el dibujado. No es una imagen completa: hay que extraer las teselas y reconstruir su posición.

```bash
git clone https://github.com/ANSSI-FR/bmc-tools
python3 bmc-tools/bmc-tools.py -s . -d bitmaps
```

La herramienta informa de más de 1.000 teselas extraídas.

## Análisis del código

`bmc-tools` parsea el formato BMCache y exporta cada tesela como BMP. La opción `-b` genera un collage con todas las teselas, pero el orden puede no ser el original.

```bash
python3 bmc-tools/bmc-tools.py -s . -d bitmaps -b
```

## Explicación del fallo

La caché conserva contenido visual aunque no haya captura de pantalla. Un atacante con acceso al perfil puede leer datos sensibles que el usuario vio, y un analista puede reconstruirlos. El reto demuestra que borrar la imagen no borra la caché.

## Reproducción local

```bash
mkdir png
mogrify -format png bitmaps/*.bmp
```

Se revisan las teselas y el collage. Las zonas con texto se amplían y se ordenan manualmente si el collage no respeta la posición.

## Explotación

No hay exploit remoto. La “explotación” es la reconstrucción visual: identificar las teselas con caracteres y unirlas hasta leer la flag. Se verifica en la plataforma y se redacta.

## Evidencia

- `file` de los ficheros de caché.
- Número de teselas extraídas.
- Collage con la zona sensible difuminada.

## Lecciones aprendidas

- La caché RDP conserva texto e imágenes de la sesión.
- `bmc-tools` es el estándar para extraer teselas.
- El collage no siempre respeta el orden; hay que revisar manualmente.
- La evidencia visual puede sobrevivir al cierre de la sesión.

## Mitigaciones y detección

- Limpiar la caché RDP al cerrar sesiones sensibles.
- Restringir el acceso físico y lógico al perfil.
- Usar escritorios remotos con políticas de retención mínima.
- Detección: acceso anómalo a `Cache*.bin` y a la caché de mapas de bits.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/no-place-to-hide/>
- <https://github.com/ANSSI-FR/bmc-tools>
- <https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-features>
