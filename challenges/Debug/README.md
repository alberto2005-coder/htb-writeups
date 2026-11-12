---
challenge: Debug
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, logic-analyzer, serial, cyber-apocalypse]
---

# Debug — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una captura de analizador lógico contiene una línea UART. Configurando el analizador serie asíncrono a 115200 baudios se decodifica el arranque y la consola imprime la flag.

## Enunciado y superficie

- Hardware, Easy, retirado (Cyber Apocalypse 2023).
- Se entrega `hw_debug.sal`.
- No hay servicio remoto.

```bash
file hw_debug.sal
```

## Reconocimiento

Se abre la captura en Logic 2. Hay dos señales, `TX` y `RX`; solo una muestra actividad. Se identifica el pin de transmisión del dispositivo.

## Análisis

1. Se añade el analizador `Async Serial`.
2. Se prueban baudios estándar: 9600, 19200, 38400, 57600, 115200.
3. 115200 produce texto legible.
4. Se exportan los bytes y se convierten de hex a ASCII.
5. La consola de arranque muestra la flag en varias líneas.

```bash
# Exportar bytes y decodificar
python3 -c "print(bytes.fromhex('...').decode(errors='replace'))"
```

También se puede copiar el texto directamente del analizador y unir las líneas.

## Explicación del fallo

La consola de depuración UART queda accesible y sin autenticación, exponiendo el arranque y secretos. No hay protección física ni desactivación del puerto.

## Reproducción local

1. Abrir la captura.
2. Añadir Async Serial en el canal activo.
3. Ajustar 115200 8N1.
4. Exportar/decodificar.
5. Reconstruir la flag.

## Evidencia

- Captura y configuración del analizador.
- Texto decodificado.
- Flag redactada.

## Lecciones aprendidas

- UART es un protocolo serie asíncrono simple.
- La velocidad correcta es clave para decodificar.
- Las consolas de depuración suelen imprimir secretos.
- El análisis de señales no requiere el hardware.

## Mitigación y detección

- Deshabilitar consolas de depuración en producción.
- Proteger físicamente los pads UART.
- No imprimir secretos en el arranque.
- Firmar/verificar el firmware.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/debug/>
- <https://www.saleae.com/>
- <https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter>
