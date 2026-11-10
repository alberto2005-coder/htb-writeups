---
challenge: Perfect Synchronization
category: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, substitution, frequency-analysis, custom-cipher]
type: Crypto
---

# Perfect Synchronization — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; el flag no se publica.

## Enunciado

Se entrega un texto cifrado y el fragmento de código que lo generó. No hay que romper AES: hay que entender qué hizo realmente el script.

## Qué hace el cifrado

El script toma **cada carácter por separado**, le suma un **salt de 15** y escribe el resultado:

```python
salt = 15
cifrado = ''.join(chr(ord(c) + salt) for c in texto)
```

Es una **sustitución por carácter**: cada letra del texto plano se convierte siempre en la misma letra del texto cifrado. No hay bloques, no hay clave, no hay ECB: la «sincronización perfecta» del nombre es el propio defecto.

```python
# descifrar
claro = ''.join(chr(ord(c) - 15) for c in cifrado)
```

## Resolverlo

1. Aplicar el desplazamiento inverso — si el salt se conoce, el reto termina aquí.
2. Si el salt no se diera, la estructura de sustitución simple permite **análisis de frecuencias**: las letras más repetidas del cifrado corresponden a las del idioma del texto (`e`, `a`, `o` en español; `e`, `t`, `a` en inglés).
3. Para textos cortos o con muchas palabras conocidas, el patrón de repetición se resuelve con **quipqiup** o un solucionador de criptogramas.

```bash
python3 - <<'PY'
ct = open('cifrado.txt').read().strip()
print(''.join(chr(ord(c) - 15) for c in ct))
PY
```

## Conclusiones

- No es un cifrado: es un **desplazamiento/sustitución monoalfabética** disfrazado de esquema moderno.
- El nombre del reto describe el fallo: cada carácter se transforma siempre igual, así que el patrón se conserva.
- Con el salt a la vista no hace falta criptoanálisis; sin él, frecuencias y patrones bastan.

## Lecciones

- Leer el código del cifrado ahorra horas de suponer AES/ECB.
- Repetir transformación por carácter = conservar estructura del lenguaje.
- Un salt fijo y público no aporta seguridad ninguna.
- Mitigación: cifrado autenticado real (AES-GCM) con clave secreta y nonce único; nunca «sumar un número» a cada carácter.
