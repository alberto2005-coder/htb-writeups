---
challenge: Weak RSA
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, rsa, wiener, factorization, openssl]
---

# Weak RSA — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto documentado; sin flags reales.
> Ficha de referencia basada en writeups técnicos. No se publican claves ni el criptograma.

## TL;DR

El reto entrega una clave pública RSA y un fichero cifrado. El módulo es demasiado pequeño o el exponente privado cumple las condiciones del ataque de **Wiener**, así que la clave privada se recupera a partir de la pública. Con la clave privada se descifra `flag.enc` y se obtiene la flag.

## Enunciado y superficie

- Crypto, Very Easy, retirado.
- Se descarga `Weak RSA.zip`, que contiene `key.pub` y `flag.enc`.
- El enunciado solo pide descifrar el mensaje.

```bash
unzip 'Weak RSA.zip'
file key.pub flag.enc
```

## Reconocimiento

```bash
openssl rsa -pubin -in key.pub -text -noout
```

La salida muestra el módulo `n` y el exponente público `e`. Si `n` es pequeño, se factoriza; si `e` es enorme y `d` es pequeño, el ataque es Wiener. También se puede usar `RsaCtfTool`, que prueba varias debilidades:

```bash
python3 RsaCtfTool.py --publickey key.pub --private
```

## Análisis del código

No hay código: el fallo es de parámetros criptográficos. RSA es seguro solo si `n = p·q` es suficientemente grande y si `d` no es pequeño. Un módulo de pocos bits se factoriza en segundos; un `d` pequeño permite aproximar `e/n` con fracciones continuas.

```text
n = p * q
φ(n) = (p - 1)(q - 1)
d = e^(-1) mod φ(n)
m = c^d mod n
```

## Explicación del fallo

Wiener demuestra que si `d < n^(1/4)/3`, `d` aparece entre los convergentes de `e/n`. `RsaCtfTool` implementa esa comprobación y, si falla, prueba factorizaciones y ataques de primos comunes. La vulnerabilidad no está en el cifrado, sino en la generación de claves.

## Reproducción local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install pycryptodome gmpy2
python3 RsaCtfTool.py --publickey key.pub --private --output key.pri
```

Si se factoriza manualmente, se reconstruye la clave con `pow(c, d, n)` o se genera un PEM con `PyCryptodome`.

## Explotación

```bash
openssl pkeyutl -decrypt -inkey key.pri -in flag.enc -out flag.txt
```

Si el cifrado es RSA "raw" (sin relleno), el descifrado directo con Python es más fiable:

```python
from Crypto.Util.number import long_to_bytes
m = pow(c, d, n)
print(long_to_bytes(m))
```

La salida correcta empieza por el formato de flag de HTB; se comprueba sin publicar el valor.

## Evidencia

- `openssl rsa -pubin -text -noout` con el módulo truncado.
- Ejecución de RsaCtfTool mostrando el ataque detectado.
- `flag.txt` con la flag redactada.

## Lecciones aprendidas

- RSA no es "seguro" solo por usar RSA: importan el tamaño del módulo y la generación de `d`.
- `RsaCtfTool` acelera el triaje, pero conviene entender qué ataque ha aplicado.
- Un cifrado raw no lleva relleno; el descifrado puede necesitar `pow` en lugar de `openssl pkeyutl`.
- No se debe reutilizar una clave pública débil en producción.

## Mitigaciones y detección

- Usar módulos de al menos 2048 bits y generadores CSPRNG.
- No usar `d` pequeño; delegar en bibliotecas probadas (OpenSSL, WebCrypto).
- Rotar claves si se detecta un módulo factorizable o un `e` anómalo.
- La detección es preventiva: escaneo de claves débiles y políticas de longitud mínima.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/weak-rsa/>
- <https://github.com/RsaCtfTool/RsaCtfTool>
- <https://en.wikipedia.org/wiki/Wiener%27s_attack>
