---
challenge: Secure Digital
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, spi, microsd, logic-analyzer, file-carving]
---

# Secure Digital — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se captura el bus SPI de una tarjeta microSD con un analizador lógico. Decodificando las líneas MISO/MOSI/CLK/CS se reconstruye la lectura del sector y se extrae la imagen; dentro está la flag.

## Enunciado y superficie

- Hardware, Easy, retirado.
- Se entrega una captura de analizador lógico (`.sal`/`.logicdata`) o un volcado SPI.
- No hay servicio remoto.

```bash
file secure_digital.sal
```

## Reconocimiento

Se abre la captura en Logic 2/Saleae. Se identifican cuatro canales: `CLK`, `CS`, `MOSI` y `MISO`. La tarjeta responde en modo SPI tras el comando `CMD0`/`CMD8`.

## Análisis

1. Se añade el analizador SPI con `CS` activo bajo y muestreo en el flanco correcto.
2. Se configura el orden de bits (MSB) y el ancho de palabra (8 bits).
3. Se exportan los bytes de MISO.
4. Se reconstruye la secuencia de comandos `CMD17` (lectura de bloque) y los datos devueltos.
5. Se concatenan los bloques y se busca una firma de sistema de archivos.

```bash
binwalk -e sdcard.bin
strings -n 6 sdcard.bin | less
```

## Explicación del fallo

La captura expone el contenido de la tarjeta sin cifrado ni autenticación. El bus SPI es accesible físicamente y no protege los datos en reposo.

## Reproducción local

1. Abrir la captura y decodificar SPI.
2. Exportar MISO a binario.
3. Recortar bloques de 512 bytes.
4. Montar o analizar la imagen resultante.

```bash
sudo mount -o loop,ro sdcard.bin /mnt/sd
```

## Evidencia

- Captura original y configuración del analizador.
- Imagen reconstruida y salida de `binwalk`.
- Flag redactada.

## Lecciones aprendidas

- SPI es un bus síncrono simple de decodificar.
- `CS` delimita las transacciones.
- Los comandos SD siguen un formato predecible.
- La extracción física no requiere credenciales.

## Mitigación y detección

- Cifrar datos sensibles en medios extraíbles.
- Usar arranque seguro/verificación de firmware.
- Restringir acceso físico y sellar puertos.
- Auditar extracción de medios.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/secure-digital/>
- <https://www.saleae.com/>
- <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface>
