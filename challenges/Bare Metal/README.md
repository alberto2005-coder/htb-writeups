---
challenge: Bare Metal
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, avr, firmware, bit-bang, disassembly]
---

# Bare Metal — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

Firmware dump de un microcontrolador AVR en formato Intel HEX. No hay sistema operativo ni consola: el programa hace *bit-bang* de datos por un pin. Se desensambla con `avr-objdump`, se identifican las dos instrucciones que marcan cada bit y se reconstruye el flujo hasta la flag.

## Enunciado y superficie

Se entrega el volcado del firmware de un microcontrolador y hay que averiguar qué transmite. Categoría Hardware, dificultad Easy.

## Reconocimiento

```bash
file firmware.hex
head -3 firmware.hex                  # formato Intel HEX (:10....)
avr-objdump -D -m avr firmware.hex | head -60
```

## Análisis del código

- El volcado no es un rootfs: `binwalk` no separa ninguna imagen y no hay tabla de particiones.
- El desensamblado muestra un bucle corto con dos instrucciones que alternan un pin de salida: patrón de *bit-bang*.
- El resto del firmware es relleno; la secuencia de bits es el mensaje.

## Explicación del fallo

No hay vulnerabilidad: el reto es reversing de firmware. El error de partida es asumir que todo volcado es una imagen Linux; aquí el dato está en la lógica del programa, no en un sistema de ficheros.

## Reproducción local

```bash
avr-objdump -D -m avr firmware.hex > disasm.txt
# si el volcado llega como binario:
avr-objdump -D -b binary -m avr firmware.bin
```

## Explotación

1. Localizar el bucle que escribe el pin (`OUT`, `SBI`/`CBI` sobre `PORTx`).
2. Traducir cada iteración a `0` o `1` según cuál de las dos instrucciones la abre.
3. Agrupar en bytes (MSB o LSB primero, según el bucle) y decodificar como ASCII.

```python
bits = [1, 0, 1, 0]        # extraídos del desensamblado
data = bytes(int("".join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits) - 7, 8))
print(data)
```

## Evidencia

- `avr-objdump` con el bucle de escritura del pin.
- Secuencia de bits y bytes reconstruidos hasta texto legible.

## Lecciones aprendidas

- **"Firmware" no siempre es una imagen Linux**: un `.hex` de microcontrolador se lee desensamblando, no con `binwalk`.
- **Dos instrucciones bastan para filtrar un mensaje**: el *bit-bang* deja el dato en el orden de escritura.
- **El orden de bits importa**: probar MSB y LSB antes de dar el flujo por perdido.

## Mitigaciones y detección

- Proteger el acceso físico y el puerto de depuración frente a la lectura del firmware.
- Firmar el firmware y verificar la firma al arrancar; cifrar los binarios distribuidos.

## Referencias

- [MITRE T1542.001](https://attack.mitre.org/techniques/T1542/001/)
- [MITRE T1552.001](https://attack.mitre.org/techniques/T1552/001/)
