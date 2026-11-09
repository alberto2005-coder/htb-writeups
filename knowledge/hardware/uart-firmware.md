# Hardware: UART, firmware y extracción

[🇬🇧 English](uart-firmware.en.md) | **Español**

Nota para retos de Hardware y para analizar un dispositivo embebido real: cómo leer la consola y cómo abrir el firmware.

## 1. Identificar la placa

- Silkscreen: modelo, revisión y a veces los pads (`TX`, `RX`, `GND`, `3V3`).
- Chips: SoC, flash SPI (Winbond, Macronix) y a veces un header de depuración (JTAG/SWD).
- Buscar el `FCC ID` en la placa y consultar las fotos internas en la base de datos de la FCC.

## 2. UART

| Señal | Cómo encontrarla |
|---|---|
| GND | continuidad con el chasis o con el negativo del conector |
| VCC | 3.3 V o 5 V con multímetro; no conectar aún |
| TX | nivel alto en reposo, pulsa al arrancar |
| RX | nivel alto; recibe lo que envías |

```bash
ls /dev/ttyUSB*
picocom -b 115200 /dev/ttyUSB0
```

- Probar `115200`, `57600`, `38400`, `9600`; en placas nuevas también `921600` y `4000000`.
- `TX` del adaptador → `RX` de la placa; `GND` común; **nunca** `VCC` del adaptador si la placa ya tiene alimentación.
- Nivel **3.3 V**; 5 V puede dañar el SoC.

## 3. Arranque

- U-Boot: parar con una tecla al inicio y probar `printenv`, `bootargs`, `init=/bin/sh`.
- Kernel: mirar la línea de comandos y la consola (`console=ttyS0,115200`).
- Login: usuario `root`/`admin` y contraseña del rootfs o de un script de inicio.

## 4. Firmware

```bash
file firmware.bin
binwalk firmware.bin
binwalk -e --run-as=root firmware.bin
unblob firmware.bin
```

- `binwalk` reconoce SquashFS, JFFS2, UBIFS, LZMA, gzip y tablas de particiones.
- Si no extrae, localizar las cabeceras mágicas a mano (`hsqs`, `UBI#`, `\x1f\x8b`) y cortar con `dd`.
- Montar: `unsquashfs -d rootfs <imagen>` o `ubireader_extract_images`.

## 5. Dentro del rootfs

```bash
grep -R -n -i "password\|passwd\|admin" rootfs/etc rootfs/usr 2>/dev/null | head
cat rootfs/etc/shadow
find rootfs -name "*.sh" -o -name "*.conf" | head
```

- Scripts de arranque con credenciales en claro.
- Claves SSH y certificados.
- Servicios expuestos (`telnetd`, `dropbear`, `httpd`) y sus configuraciones.

## 6. Lectura directa de flash

Si no hay UART:

- **SPI**: clip SOIC-8 y `flashrom -p ch341a_spi -r dump.bin`.
- **eMMC**: `mmc-utils` o un adaptador; a veces hay puntos `CLK/CMD/DAT0`.
- **JTAG/SWD**: OpenOCD con la config del SoC.

## Errores típicos

- **Basura en consola** → `GND` mal o baudios incorrectos; no es la placa.
- **Sin salida** → `TX`/`RX` cruzados o consola deshabilitada en el firmware.
- **`binwalk` no reconoce** → imagen cifrada o comprimida con LZMA propietario; usa `unblob` o firmas propias.
- **Arranque verifica firma** → no se puede modificar el rootfs; busca la consola o el bootloader.

MITRE: T1542.001, T1552.001, T1005.
