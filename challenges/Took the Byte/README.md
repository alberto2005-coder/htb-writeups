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

Se entrega un único fichero llamado `password`, sin extensión útil. `file` no lo reconoce y `xxd | head` muestra un patrón muy repetido: casi todos los bytes son `0xFF`, salvo el principio.

## Análisis del código

No hay código: el «cifrado» es un **XOR de un byte** aplicado al fichero original. Se detecta por la repetición de `0xFF` y por la ausencia de cabeceras conocidas; la transformación es simétrica, así que la misma operación lo deshace.

## Explicación del fallo

Te dan un fichero llamado `password` que no abre con nada. Su contenido es casi todo `0xFF`: un **XOR con la clave `0xFF`** lo devuelve a la vida y aparece un **ZIP** con `password.txt`, que contiene la flag.

## Reproducción local

```bash
python3 - <<'PY'
data = open('password','rb').read()
open('out.bin','wb').write(bytes(b ^ 0xFF for b in data))
PY
file out.bin      # Zip archive data
unzip -o out.bin && cat password.txt
```

Si la clave no fuese `0xFF`, basta probar las 256 posibles y quedarse con la que produzca una firma válida (`PK`, `%PDF`, `\x89PNG`).

## Explotación

1. `xxd password | head` confirma el muro de `ff`.
2. Se aplica el XOR con `0xFF` a **todo** el fichero (no sólo a la cabecera).
3. `file out.bin` devuelve `Zip archive data`; `unzip` extrae `password.txt` con la flag.

## Evidencia

- Un único fichero, `password`, sin extensión útil.

## Lecciones aprendidas

- **Esperar criptografía**: es un XOR de un byte, no hay que buscar contraseñas ni usar `rockyou`.
- **`strings`**: con el fichero sin decodificar no muestra nada útil; engaña.

- Un XOR de un byte se detecta por la repetición de un valor y se rompe probando 256 claves.
- La firma de un formato (`PK`, `%PDF`, `\x89PNG`) sirve para verificar que la transformación fue correcta.
- «Ofuscado» no es «cifrado»: un byte de distancia separa el ruido del fichero original.

## Mitigaciones y detección

- Un XOR de un byte no es cifrado: para datos sensibles, AES-GCM con clave gestionada fuera del artefacto.
- No reutilizar una única clave de un byte para todo el fichero: es un cifrado César sobre bytes y se rompe por frecuencia.
- Detección: ficheros con entropía anómalamente baja o un byte dominante, y adjuntos sin firma reconocible.
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
