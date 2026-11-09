---
challenge: Took the Byte
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, xor, zip, magic-bytes, cyberchef]
type: Forensics
---

# Took the Byte — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Te dan un fichero llamado `password` que no abre con nada. Su contenido es casi todo `0xFF`: un **XOR con la clave `0xFF`** lo devuelve a la vida y aparece un **ZIP** con `password.txt`, que contiene la flag.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Te dan un fichero llamado `password` que no abre con nada. Su contenido es casi todo `0xFF`: un **XOR con la clave `0xFF`** lo devuelve a la vida y aparece un **ZIP** con `password.txt`, que contiene la flag.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Un único fichero, `password`, sin extensión útil.

## Lecciones aprendidas

- **Esperar criptografía**: es un XOR de un byte, no hay que buscar contraseñas ni usar `rockyou`.
- **`strings`**: con el fichero sin decodificar no muestra nada útil; engaña.

- Un XOR de un byte se detecta por la repetición de un valor y se rompe probando 256 claves.
- La firma de un formato (`PK`, `%PDF`, `\x89PNG`) sirve para verificar que la transformación fue correcta.
- «Ofuscado» no es «cifrado»: un byte de distancia separa el ruido del fichero original.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Método

1. **Ver qué es**:

```bash
file password
xxd password | head
binwalk password
```

`file` no lo reconoce y `xxd` muestra una avalancha de `ff`: la firma típica de un XOR con `0xFF`.

2. **Aplicar el XOR** (el nombre del reto es la pista: «took a byte»):

```bash
python3 -c "d=open('password','rb').read(); open('out','wb').write(bytes(b^0xFF for b in d))"
file out
```

3. **Abrir el ZIP** resultante:

```bash
unzip out
cat password.txt
```

La flag está en el texto. En CyberChef equivale a *XOR* con clave `ff` seguido de *Unzip*.

4. **Comprobación de firma**: el ZIP empieza por `PK\x03\x04`; si tras el XOR no aparece, se ha usado la clave equivocada (probar `0x00`, `0xFF` y un bruteforce de un byte).
