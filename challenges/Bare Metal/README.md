---
challenge: Bare Metal
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, firmware, binwalk, flash]
---

# Bare Metal — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

- Ver las secciones adyacentes para el detalle.

## Enunciado y superficie

Se entrega una imagen de firmware de un dispositivo embebido. Hay que localizar la consola serie y extraer la información del sistema: credenciales, servicios y la flag.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

[🇬🇧 English](README.en.md) | **Español**

## Reproducción local

- Reproduce el firmware en QEMU o sobre el dispositivo; consola UART a 3.3 V.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **No hay salida en UART** → `TX`/`RX` invertidos o baudios incorrectos; prueba también 4 Mbps en placas modernas.
- **Caracteres basura** → masa común mal conectada o nivel lógico distinto (1.8 V).
- **`binwalk -e` no extrae** → imagen cifrada o comprimida con LZMA propietario; usa `unblob` o extrae a mano con los offsets.
- **Login rechazado** → la contraseña está en el rootfs; no la fuerces por la consola.

- El firmware suele contener la contraseña antes que la consola.
- `GND` primero, luego `TX`/`RX`; un cable mal puesto no rompe nada, pero no da salida.
- Las imágenes modernas vienen firmadas: comprobar si el arranque verifica la firma.

MITRE: T1542.001, T1552.001.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [MITRE T1542.001](https://attack.mitre.org/techniques/T1542/)
- [MITRE T1552.001](https://attack.mitre.org/techniques/T1552/)
- [MITRE T1542.001](https://attack.mitre.org/techniques/T1542/001/)
- [MITRE T1552.001](https://attack.mitre.org/techniques/T1552/001/)
- [uart-firmware](../../knowledge/hardware/uart-firmware.md)
## Triaje del firmware

```bash
file firmware.bin
binwalk firmware.bin
binwalk -e firmware.bin
strings -a firmware.bin | grep -i -E "uart|console|baud|root|passwd"
```

`binwalk -e` separa el sistema de ficheros (SquashFS, JFFS2, UBIFS). Si es una imagen completa, aparecen tabla de particiones, kernel y rootfs.

## Consola UART

1. **Localizar pines**: `TX`, `RX`, `GND` (y a veces `VCC`) suelen estar rotulados o agrupados en una fila de 3-4 pads. `GND` se identifica por continuidad con el chasis.
2. **Adaptador**: USB-TTL a **3.3 V** (nunca 5 V sin comprobar). `TX` del adaptador al `RX` de la placa y viceversa; `GND` común.
3. **Baudios**: probar `115200 8N1` primero, luego `57600`, `38400`, `9600`. Con `picocom`:

   ```bash
   picocom -b 115200 /dev/ttyUSB0
   ```

4. **Arranque**: al encender aparece el bootloader (U-Boot). Si permite `init=/bin/sh` o una consola, se obtiene shell sin credenciales.
5. **Login**: si pide usuario y contraseña, se buscan en el rootfs (`/etc/shadow`, `/etc/passwd`) tras montarlo.

## Extraer del rootfs

```bash
unsquashfs -d rootfs squashfs-root.squashfs
grep -R "password\|admin" rootfs/etc 2>/dev/null | head
cat rootfs/etc/shadow
```

Con `/etc/shadow` y `john`/`hashcat` se recuperan contraseñas débiles; muchas imágenes traen la de `root` en claro en scripts de inicio.
