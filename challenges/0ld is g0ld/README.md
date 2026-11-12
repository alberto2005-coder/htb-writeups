---
challenge: 0ld is g0ld
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, pdf, john, morse, stego]
---

# 0ld is g0ld — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin contraseña ni flag reales.

## TL;DR

Un PDF protegido con contraseña. `pdf2john` extrae el hash, `john` lo crackea con `rockyou.txt` y el PDF revela un retrato con una tira de código Morse. Al decodificarla se obtiene la flag.

## Enunciado y superficie

- Misc, Easy, retirado.
- Se entrega `0ld is g0ld.pdf`.
- El PDF pide una contraseña para abrirse.

```bash
file '0ld is g0ld.pdf'
pdfinfo '0ld is g0ld.pdf'
```

## Reconocimiento

```bash
pdf2john '0ld is g0ld.pdf' > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

`pdf2john` genera un hash compatible con John. La contraseña aparece en la salida; no se publica.

## Análisis del código

No hay código: el reto combina cracking de PDF y esteganografía visual. Al abrir el documento se ve un retrato; al hacer zoom se distingue una secuencia de puntos y rayas.

```bash
john --show hash.txt
```

## Explicación del fallo

La contraseña del PDF es débil y está en un diccionario común. Una vez abierto, el mensaje está oculto en la imagen, no en metadatos ni en una capa separada. La “seguridad” depende de dos capas triviales.

## Reproducción local

```bash
xdg-open '0ld is g0ld.pdf'
```

Se recorta la zona del código Morse y se decodifica con una tabla o una herramienta online/offline. El resultado tiene el formato de flag de HTB.

## Explotación

No hay servidor. La explotación es pasiva: crackear, abrir, leer el Morse y decodificar. Se verifica en la plataforma y se redacta.

## Evidencia

- `pdf2john` y `john --show` con la contraseña redactada.
- Captura del retrato con el Morse visible.
- Texto decodificado con la flag redactada.

## Lecciones aprendidas

- `pdf2john` + `john` es un flujo estándar para PDF débiles.
- La esteganografía visual no requiere herramientas complejas.
- El zoom y el contraste son suficientes para leer el mensaje.
- La contraseña del PDF no protege el contenido una vez crackeada.

## Mitigaciones y detección

- Usar contraseñas fuertes y AES-256 para PDFs sensibles.
- No ocultar secretos en imágenes sin cifrado adicional.
- Rotar cualquier secreto expuesto en un PDF.
- Detección: acceso masivo a PDFs y ejecución de `pdf2john`/`john`.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/misc/0ld-is-g0ld/>
- <https://www.openwall.com/john/>
- <https://en.wikipedia.org/wiki/Morse_code>
