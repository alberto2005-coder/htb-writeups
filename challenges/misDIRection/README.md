---
challenge: misDIRection
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, zip, directory-structure, base64, scripting]
---

# misDIRection — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flag real.

## TL;DR

Un ZIP contiene una jerarquía `.secret/` con directorios nombrados por caracteres y ficheros nombrados por posiciones. Al ordenar numéricamente los ficheros y concatenar el nombre de su directorio se obtiene una cadena base64; al decodificarla aparece la flag.

## Enunciado y superficie

- Misc, Very Easy, retirado.
- Se entrega `misDIRection.zip`.
- El ZIP está protegido con la contraseña habitual del reto.

```bash
file misDIRection.zip
unzip -l misDIRection.zip | head
```

## Reconocimiento

```bash
unzip -P '<ZIP_PASSWORD>' misDIRection.zip
find .secret -type f | head
```

La estructura contiene directorios como `.secret/S/`, `.secret/V/`, etc., y ficheros con nombres numéricos (`1`, `35`, `2`...). No hay contenido dentro de los ficheros: el nombre es el dato.

## Análisis del código

Cada fichero representa una posición y su directorio el carácter que ocupa. Al ordenar por el número del fichero se reconstruye la secuencia:

```bash
find .secret -type f | awk -F / '{ print $3, $2 }' | sort -n | awk '{ print $2 }' | tr -d '\n'
```

El resultado es una cadena que parece base64. Se decodifica:

```bash
... | base64 -d
```

## Explicación del fallo

La información está codificada en los nombres, no en el contenido. La “protección” es solo la contraseña del ZIP, que es débil/conocida. Cualquiera con la estructura puede reconstruir el mensaje sin abrir los ficheros.

## Reproducción local

```bash
unzip -P '<ZIP_PASSWORD>' misDIRection.zip -d work
cd work
find .secret -type f | awk -F / '{ print $3, $2 }' | sort -n | awk '{ print $2 }' | tr -d '\n' > out.b64
base64 -d out.b64
```

Se comprueba que el orden numérico es correcto y que no hay posiciones repetidas.

## Explotación

No hay servidor. La explotación es reconstruir la cadena y decodificarla. La flag se verifica en la plataforma y se redacta.

## Evidencia

- Estructura de directorios y ficheros.
- Cadena base64 redactada.
- Flag redactada.

## Lecciones aprendidas

- Los nombres de ficheros y directorios son datos.
- `find` + `awk` + `sort -n` reconstruye secuencias por posición.
- Un ZIP con contraseña débil no protege la estructura.
- La codificación base64 es una pista habitual.

## Mitigaciones y detección

- No usar nombres de ficheros para almacenar secretos.
- Cifrar el archivo completo con una contraseña fuerte.
- Evitar estructuras que revelen el mensaje sin abrir el contenido.
- Detección: en CTF, revisar metadatos y nombres; en producción, DLP sobre archivos.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/misc/misdirection/>
- <https://linux.die.net/man/1/find>
- <https://en.wikipedia.org/wiki/Base64>
