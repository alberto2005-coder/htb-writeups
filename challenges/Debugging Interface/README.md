---
challenge: Debugging Interface
type: Hardware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, saleae, logic-analyzer, serial]
---

# Debugging Interface — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se captura una interfaz serie asíncrona (UART) de un dispositivo embebido. El archivo `.sal` es un ZIP de Saleae Logic con `digital-0.bin` y `meta.json`. Midiendo el pulso más corto se obtiene un baudaje de 31250; al decodificar la línea como UART aparece el mensaje con la flag.

## Enunciado y superficie

- Hardware, Very Easy, retirado.
- Se entrega `debugging_interface_signal.sal`.
- Un solo canal digital.

```bash
file debugging_interface_signal.sal
unzip -l debugging_interface_signal.sal
```

## Reconocimiento

```bash
unzip debugging_interface_signal.sal -d sal
ls sal
# digital-0.bin  meta.json
```

`digital-0.bin` no sigue el formato de exportación documentado por Saleae; hay que interpretarlo como una traza de transiciones. El `meta.json` indica la frecuencia de muestreo (50 MS/s).

## Análisis

Se carga el `.sal` en Saleae Logic o se parsea `digital-0.bin` para reconstruir los tiempos de flanco. El pulso más corto ronda los 32 µs:

```text
bit = 1 / 31250 ≈ 32 µs
```

Se configura el decodificador `Async Serial` en el canal 0 con 31250 baudios, 8 bits de datos, sin paridad y 1 bit de parada. La salida es texto ASCII con la flag.

Alternativa sin Saleae:

```python
# Leer transiciones, agrupar por duración de bit y muestrear 8 bits por carácter
```

## Explicación del fallo

La interfaz de depuración UART queda accesible y transmite datos en claro, incluida información sensible. No hay autenticación ni cifrado en el enlace serie.

## Reproducción local

1. Extraer el `.sal`.
2. Medir el periodo de bit.
3. Decodificar como UART 31250 8N1.
4. Exportar el texto y localizar el patrón de flag.

## Evidencia

- `file`/`unzip` del `.sal`.
- Medición del periodo y cálculo del baudaje.
- Texto decodificado con la flag redactada.

## Lecciones aprendidas

- UART es un protocolo habitual en depuración embebida.
- El baudaje se deduce del pulso más corto.
- Los `.sal` son ZIP con datos binarios.
- La instrumentación física puede revelar secretos.

## Mitigación y detección

- Deshabilitar UART de depuración en producción.
- Proteger los pads con contraseña o fusibles.
- No transmitir secretos por interfaces serie.
- En laboratorio, documentar la captura y el baudaje.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/debugging-interface/>
- <https://support.saleae.com/>
- <https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter>
