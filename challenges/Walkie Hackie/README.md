---
challenge: Walkie Hackie
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, rf, iq, signal, demodulation]
---

# Walkie Hackie — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega una captura IQ de una comunicación de radio. Se identifica la frecuencia central y el ancho de banda, se demodula la señal y se decodifican los tonos o la voz para recuperar la flag.

## Enunciado y superficie

- Hardware, Easy, retirado.
- Se entrega un archivo IQ (`complex16s` o similar).
- El enunciado menciona un walkie-talkie.

```bash
file capture.iq
python3 -c 'import numpy as np; print(np.fromfile("capture.iq", dtype=np.complex64)[:5])'
```

## Reconocimiento

- Abrir la captura en `inspectrum` o `Universal Radio Hacker`.
- Identificar la portadora y el ancho de banda.
- Revisar el espectrograma en busca de ráfagas y saltos.
- Determinar el tipo de modulación (FM, AM, FSK).

## Análisis de la señal

La señal es FM de banda estrecha. Se desplaza la frecuencia central a baseband, se aplica un demodulador FM y se filtra el audio. Si la voz no es inteligible, se prueban factores de decimación y se revisan los tonos DTMF.

```python
import numpy as np
from scipy.signal import butter, filtfilt

iq = np.fromfile('capture.iq', dtype=np.complex64)
audio = np.angle(iq[1:] * np.conj(iq[:-1]))
```

## Explicación del fallo

La comunicación no está cifrada. La captura contiene suficiente información para demodular y escuchar o decodificar el mensaje; la única dificultad es identificar los parámetros de la señal.

## Reproducción local

```bash
inspectrum -r 1e6 capture.iq
# Ajustar frecuencia, ancho de banda y demodulación
```

## Explotación

Se guarda el audio demodulado, se reproduce y se transcribe el mensaje. La flag puede estar en la voz, en tonos DTMF o en un texto modulado.

## Evidencia

- Espectrograma con la portadora.
- Audio demodulado inteligible.
- Tonos o texto decodificado.
- Flag redactada.

## Lecciones aprendidas

- Una captura IQ conserva toda la señal.
- La demodulación FM es una resta de fases.
- Los tonos DTMF se decodifican con Goertzel.

## Mitigaciones y detección

- Usar radios con cifrado y autenticación.
- No transmitir secretos por canales analógicos.
- Monitorizar emisiones no autorizadas.
- Referencias: GNU Radio, Inspectrum, HTB Walkie Hackie.

## Referencias

- <https://www.hackthebox.com/challenges/Walkie%20Hackie>
- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/walkie-hackie/>
- <https://github.com/gnuradio/gnuradio>
- <https://attack.mitre.org/techniques/T1040/>
