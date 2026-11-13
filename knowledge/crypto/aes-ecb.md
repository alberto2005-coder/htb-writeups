---
topic: AES ECB
tags: [crypto, aes, ecb, block-cipher, pattern-leak, padding]
---

# AES ECB

[🌐 English](aes-ecb.en.md) | **Español**

## Concepto

AES-ECB cifra cada bloque de 16 bytes de forma independiente. Los bloques iguales producen el mismo ciphertext, por lo que el modo filtra patrones y estructura. No es un cifrado seguro para datos con repetición, aunque se encuentre en apps y protocolos heredados.

## Cuándo aplica

- Ciphertext con bloques repetidos.
- Clave embebida en una app o configuración.
- Datos con campos predecibles.
- Comparación de mensajes de igual longitud.

## Procedimiento

1. Identificar el algoritmo y el modo.
2. Dividir el ciphertext en bloques de 16 bytes.
3. Buscar bloques idénticos.
4. Comparar cifrados de mensajes controlados.
5. Recuperar la clave si está embebida y descifrar.

```bash
python3 - <<'PY'
from collections import Counter
c = bytes.fromhex('<CIPHERTEXT>')
blocks = [c[i:i+16] for i in range(0, len(c), 16)]
print(Counter(blocks).most_common(5))
PY
openssl enc -d -aes-128-ecb -K <KEY> -in data.bin
```

## Variantes

- ECB con clave de 128 o 256 bits.
- Datos comprimidos antes de cifrar.
- Cifrado por bloques con IV fijo.
- Clave derivada de una contraseña débil.

## Limitaciones

- ECB no permite recuperar la clave por sí solo.
- La repetición depende de los datos.
- El padding puede ocultar el último bloque.
- Una clave aleatoria y datos únicos reducen la filtración.

## Mitigación y detección

- Usar AES-GCM o CBC con IV aleatorio y MAC.
- No cifrar datos estructurados con ECB.
- Proteger y rotar claves.
- Revisar configuraciones y bibliotecas heredadas.

## Referencias

- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://owasp.org/www-project-cryptographic-storage-cheat-sheet/>
- <https://attack.mitre.org/techniques/T1573/>
