---
sherlock: Lockpick 2.0
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
evidence: Recurso compartido cifrado y muestra de ransomware
tools: [UPX, Ghidra, CyberChef, Python]
state: Retired
tags: [dfir, análisis-de-malware]
---


# Lockpick 2.0 — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Segundo golpe del mismo grupo: han cifrado un recurso compartido y esta vez la política es **no negociar**. Hay que recuperar los ficheros analizando la muestra y la nota de rescate.

## Evidencias

- `DANGER.txt` con la advertencia y la contraseña del ZIP de la muestra.
- Un directorio `share` con los ficheros cifrados y la nota del atacante.
- `malware.zip` con el binario: un ELF llamado `update`, **empaquetado con UPX**.
- Los documentos cifrados (`expanding-horizons.pdf`, `takeover.docx`) y la nota `countdown.txt`.

## Investigación

1. **Nota de rescate**: extensión de los cifrados, importe y dirección de pago, correo o portal de contacto. Es la fuente de los IOCs.

2. **Muestra**: comprobar el empaquetado antes de nada.

```bash
upx -d sample -o sample.unpacked   # si está empaquetado
detect-it-easy sample
```

3. **Algoritmo**: `upx -d update` y, en `encrypt_file`, aparece `aes_256_cbc`. La clave y el IV están **en el propio binario** (32 y 16 bytes en hexadecimal), así que el material de descifrado se extrae del desensamblado y no de la red.

4. **Descifrar**: AES-256-CBC con esa clave e IV sobre los ficheros del `share`; se valida abriendo el PDF y el DOCX resultantes (`Australian market`, `Notionwide Bank`).

5. **Informe**: ficheros afectados, extensión, clave, ventana de cifrado y rescate exigido (un millón de libras en `countdown.txt`). El nombre del fichero de clave sale de la URL corta de la nota.

Nota de dificultad: los índices públicos la listan como Easy y algún writeup la etiqueta como Hard; se deja **Easy** y se anota la discrepancia.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- La nota de rescate es evidencia: identifica la familia y la infraestructura.
- UPX se detecta y se revierte en un comando; no es protección real.
- Recuperar sin pagar exige entender el esquema de claves, no sólo el algoritmo.

## Tropiezos

- **`DANGER.txt`**: contiene la contraseña del ZIP; sin leerlo no hay muestra.
- **Cifrado por bloques**: los ficheros grandes pueden cifrarse por tramos con IV distinto por bloque.
- **Confundir codificación con cifrado**: base64/XOR no protegen; AES con clave asimétrica sí.
