---
challenge: Mini Line
type: Hardware
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [hardware, intel-hex, firmware, reversing, uart]
---

# Mini Line — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se entrega firmware en formato Intel HEX y una captura de línea serie. Se convierte el HEX a binario, se identifica la función que valida la entrada y se reconstruye la secuencia que imprime la flag.

## Enunciado y superficie

- Hardware, Medium, retirado.
- Se entrega un `.hex` y posiblemente una captura de línea.
- No hay servicio remoto.

```bash
file firmware.hex
head firmware.hex
```

## Reconocimiento

El archivo usa el formato Intel HEX (`:LLAAAATT...CC`). Se convierte a binario con `objcopy` o `srec_cat`:

```bash
objcopy -I ihex -O binary firmware.hex firmware.bin
```

Se identifica la arquitectura con `binwalk`/`strings` y se carga en Ghidra/radare2.

## Análisis

1. Se localizan cadenas de bienvenida y mensajes de error.
2. Se sigue la función principal y la rutina de comparación.
3. Se identifica el protocolo de línea (comandos ASCII, delimitador `\n`).
4. Se reconstruye la entrada esperada o se emula la validación.
5. Se extrae la flag de la memoria o de la respuesta.

```bash
r2 -A firmware.bin
pdf @ main
```

## Explicación del fallo

La validación se implementa en firmware extraíble y la clave/flag está embebida o derivable. No hay protección criptográfica ni verificación de integridad.

## Reproducción local

1. Convertir Intel HEX a binario.
2. Identificar arquitectura y punto de entrada.
3. Analizar la rutina de comparación.
4. Emular con `qemu` o reconstruir la entrada.
5. Obtener la flag del modelo.

## Evidencia

- `.hex` original y binario generado.
- Cadenas y funciones relevantes.
- Flag redactada.

## Lecciones aprendidas

- Intel HEX incluye dirección y checksum por línea.
- El firmware suele contener mensajes que guían el análisis.
- La emulación evita ejecutar hardware real.
- La ofuscación simple no protege secretos.

## Mitigación y detección

- No almacenar secretos en firmware.
- Firmar y cifrar el firmware.
- Proteger la lectura del bus de depuración.
- Verificar integridad al arrancar.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/mini-line/>
- <https://en.wikipedia.org/wiki/Intel_HEX>
- <https://ghidra-sre.org/>
