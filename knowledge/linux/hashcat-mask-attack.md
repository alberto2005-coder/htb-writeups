---
title: Hashcat — máscaras para contraseñas con formato
tags: [linux, hashcat, password-cracking, mask, sha256]
---

# Hashcat — máscaras para contraseñas con formato

[🇬🇧 English](hashcat-mask-attack.en.md) | **Español**

## Concepto

Una máscara describe la estructura de la contraseña: caracteres fijos y posiciones variables. Es mucho más rápida que un diccionario cuando se conoce el formato (por ejemplo, `susan_nasus_` seguido de nueve dígitos).

## Cuándo aplica

- Hay un hash y una pista del formato (correo, política, ticket).
- El prefijo o sufijo es conocido.
- El espacio de búsqueda cabe en un tiempo razonable.

## Procedimiento

1. Identificar el tipo de hash con `hashid` o `hashcat --identify`.
2. Elegir el modo (`-m`) y construir la máscara.
3. Calcular el espacio: `?d` = 10, `?l` = 26, `?a` = 95.
4. Ejecutar con `-a 3` y, si hace falta, `--increment`.

```bash
hashcat hash.txt -m 1400 -a 3 'susan_nasus_?d?d?d?d?d?d?d?d?d'
hashcat hash.txt -m 1400 -a 3 -1 '?l?d' '?1?1?1?1?1?1'
```

## Variantes

- `?u` mayúsculas, `?s` símbolos, `?b` bytes.
- `--increment` prueba longitudes crecientes.
- `-O` usa el kernel optimizado si la longitud lo permite.
- Un diccionario con reglas (`-r`) puede ser mejor si hay palabras base.

## Limitaciones

- El espacio crece exponencialmente; nueve dígitos son 10^9.
- La velocidad depende de la GPU y del modo.
- Una pista incorrecta hace la búsqueda inútil.

## Mitigación y detección

- Usar contraseñas largas y aleatorias, no patrones predecibles.
- Almacenar con Argon2id/bcrypt y salt único.
- Limitar intentos y monitorizar picos de CPU/GPU.
- Revisar políticas que crean prefijos comunes.

## Referencias

- <https://hashcat.net/wiki/doku.php?id=mask_attack>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://hashcat.net/hashcat/>
