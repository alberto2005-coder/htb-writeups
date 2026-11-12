---
challenge: Call
type: Crypto
difficulty: Unknown
platform: Hack The Box
state: Retired
tags: [crypto, audio, dtmf, primes, scripting]
---

# Call — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Dificultad oficial no confirmada; ficha de referencia no jugada.
> Sin flag ni secuencia DTMF real.

## TL;DR

El reto entrega `sound.mp3`. Al convertir el audio a WAV y demodularlo con `multimon-ng` aparecen tonos **DTMF**: una secuencia de dígitos. Esa secuencia se interpreta como índices de números primos y se traduce a letras (2 = A, 3 = B, 5 = C…). El resultado es la flag.

## 1. Inspeccionar el audio

```bash
file sound.mp3
ffprobe -hide_banner sound.mp3
soxi sound.mp3
```

Se comprueba la duración, el número de canales y la frecuencia de muestreo. Los tonos DTMF se oyen como pitidos de teléfono; si el audio es largo, se localizan por espectrograma:

```bash
ffmpeg -i sound.mp3 -lavfi showspectrumpic=s=1024x512 spec.png
```

## 2. Convertir y demodular

`multimon-ng` trabaja mejor con WAV PCM mono:

```bash
ffmpeg -i sound.mp3 -ar 8000 -ac 1 -c:a pcm_s16le sound.wav
multimon-ng -t wav -a DTMF sound.wav
```

La salida es una lista de dígitos, por ejemplo `DTMF: 5` repetidos. Se limpia y se concatena:

```bash
multimon-ng -t wav -a DTMF sound.wav | grep -oE 'DTMF: [0-9]' | awk '{print $2}' | tr -d '\n'
```

Si no detecta nada, se prueba con otro filtro o se ajusta la ganancia:

```bash
sox sound.wav norm.wav norm
multimon-ng -t wav -a DTMF norm.wav
```

## 3. El cifrado de primos

Cada letra se representa por un número primo:

```text
A=2  B=3  C=5  D=7  E=11  F=13  G=17  H=19  I=23  J=29
K=31 L=37 M=41 N=43 O=47  P=53  Q=59  R=61  S=67  T=71
U=73 V=79 W=83 X=89 Y=97  Z=101
```

La secuencia DTMF da esos primos, normalmente separados por `0` o `1` (que no son primos y actúan como separadores). Se decodifica con un script:

```python
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101]
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
seq = '<DTMF_DIGITS>'.replace('0', ' ').replace('1', ' ')
out = ''.join(alphabet[primes.index(int(n))] for n in seq.split())
print(out)
```

Si la secuencia viene sin separadores, se prueba a agrupar de dos en dos o se usan los primos como posiciones.

## 4. Variantes

- **Primos como posiciones**: el número indica la posición en el alfabeto, no el valor primo.
- **A1Z26**: los dígitos DTMF se agrupan en pares y se convierten directamente (`01`=A, `02`=B…).
- **Dos capas**: DTMF → número de teléfono → coordenadas → texto. Se prueba la hipótesis más simple antes de complicarla.
- **Audio invertido**: si los tonos no decodifican, `sox sound.wav reverse.wav reverse`.

## 5. Comprobar el resultado

El texto debe ser legible y tener el formato `HTB{...}`. Si sale una palabra sin sentido, se revisa:

- El orden de los dígitos.
- Los separadores (`0`/`1`).
- Si se ha perdido un tono al recortar el audio.
- Si hay que invertir la asignación (A=101, Z=2).

## Lecciones aprendidas

- DTMF es un estándar telefónico; `multimon-ng` lo demodula sin escribir un decoder.
- Un cifrado “de primos” puede ser sustitución directa o índice; hay que probar ambas.
- El espectrograma ayuda a ver si hay tonos ocultos o ruido.
- La conversión a WAV mono evita fallos de decodificación.
- La flag se valida por formato, no por intuición.

## Mitigaciones (para retos)

- Guardar el audio original y trabajar con copias.
- Documentar la frecuencia de muestreo y el filtro usado.
- No asumir que el primer resultado es el correcto: probar el inverso.

MITRE: T1027, T1140.

## Referencias

- <https://inesmartins.github.io/htb-crypto-challenge-call/index.html>
- <https://github.com/EliasOenal/multimon-ng>
- <https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling>
