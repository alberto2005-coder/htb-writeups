---
title: Cadenas C y bytes nulos: truncado silencioso
tags: [pwn, c-strings, strcpy, null-byte, crypto, logic-bug]
---

# Cadenas C y bytes nulos: truncado silencioso

[🇬🇧 English](null-byte-truncation.en.md) | **Español**

## 1. Cuándo mirar aquí

Se copian claves, tokens o blobs binarios con `strcpy`, `strlen`, `strcmp` o `%s`. Estas funciones se detienen en el primer `\0`, así que un dato aleatorio que contenga un nulo se corta sin avisar.

## 2. La regla

Una cadena C termina en el primer byte cero:

```c
char buf[8] = { 'A', 'B', '\0', 'C', 'D', 'E', 'F', 'G' };
strlen(buf);   // 2, no 8
strcpy(dst, buf);  // copia "AB" y el terminador
```

El resto sigue en memoria, pero ninguna función de cadena lo ve. Si el búfer se reutiliza, los bytes posteriores al terminador son los de la operación anterior.

## 3. Dónde aparece el fallo

- **Claves generadas con `/dev/urandom`**: cualquier byte puede ser `\0`; la clave real es más corta que la pedida.
- **Tokens en base64**: si se decodifican a bytes, un nulo interno trunca al copiarlos.
- **Buffers sin inicializar**: `strcpy` copia el terminador y deja basura detrás, que una lectura posterior puede interpretar.
- **Comparaciones**: `strcmp` considera iguales dos cadenas que solo coinciden hasta el primer nulo.

## 4. El caso del vault

Un programa genera una clave de longitud `n` (0–31) y la copia a una global con `strcpy`. El bucle evita nulos en la posición `i`, pero no antes. Al reducir `n` de 31 a 0, el terminador se mueve al principio y la global queda vacía. El XOR con cero devuelve el texto original.

```text
n=31: [ k0 k1 ... k30 00 ]
n=2:  [ k0 k1 00 ]
n=0:  [ 00 ]
```

No hay corrupción: el programa hace exactamente lo que dicen las funciones de cadena.

## 5. Cómo detectarlo

- Revisar cada `strcpy`/`strlen` que reciba datos binarios.
- Comprobar si la longitud se guarda aparte; si no, el dato no es una cadena.
- Buscar `memset` que solo cubre parte del búfer y deja bytes antiguos.
- En una explotación, probar longitudes decrecientes y ver si el secreto cambia de tamaño.

## 6. Mitigación

- Usar `memcpy`/`memcmp` con longitud explícita y guardar `(buffer, length)`.
- Inicializar el destino completo antes de copiar (`memset(dst, 0, sizeof dst)`).
- No usar `strcpy` con datos que puedan contener `\0`; `strncpy` tampoco es la solución (no garantiza terminador).
- Para claves, usar una estructura con tamaño o un tipo que no dependa de terminadores.
- CWE-170 (improper null termination), CWE-327 (broken crypto).

## 7. Detección en producción

- Claves de longitud variable o menor de la esperada en logs.
- Errores de autenticación que desaparecen al cambiar la longitud de un token.
- Diferencias entre el tamaño declarado y `strlen` del valor.

Referencias: `man 3 strcpy`, `man 3 strlen`, CWE-170 y la documentación de `memcpy`.
