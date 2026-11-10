---
title: RSA con módulo pequeño y RSA de libro
tags: [crypto, rsa, factoring, ctf]
---

# RSA: módulo pequeño, `n` primo y exponente bajo

[🇬🇧 English](rsa-small-modulus.en.md) | **Español**

## 1. El patrón

Un reto de RSA es atacable cuando se rompe alguno de sus supuestos: `n` es demasiado pequeño (factorizable en segundos), `n` es primo (φ = n − 1), `e` es 3 y el mensaje es corto (raíz cúbica exacta), o dos módulos comparten un factor (basta un `gcd`).

Empieza siempre por leer la clave:

```bash
openssl rsa -pubin -in key.pub -text -noout
python3 -c "from Crypto.PublicKey import RSA; k=RSA.import_key(open('key.pub').read()); print(k.n.bit_length(), k.e)"
```

Menos de 1024 bits es señal de que se factoriza.

## 2. Factorizar `n`

```python
from sympy import factorint
from Crypto.Util.number import long_to_bytes

n = <n>; e = <e>; c = <c>
p, q = list(factorint(n))[:2]
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
print(long_to_bytes(pow(c, d, n)))
```

Los docs de SymPy lo dicen claro: rho y p−1 sacan factores de ~10 dígitos en segundos y `ecm` factoriza ~35 dígitos con comodidad; sin factores pequeños, un `n` de 60 dígitos no sale. Para eso, `yafu`, `msieve` o `RsaCtfTool`:

```bash
RsaCtfTool.py --publickey key.pub --uncipherfile flag.enc --private
```

## 3. Casos especiales

- **`n` primo** → φ = n − 1 («Primary Knowledge»):
  ```python
  d = pow(e, -1, n - 1)
  ```
- **`e = 3` y `m` corto** → si `m³ < n` el cifrado no llega a reducir módulo `n` (`c = m³`) y la raíz cúbica entera devuelve el mensaje:
  ```python
  from gmpy2 import iroot
  m, exact = iroot(c, 3)
  ```
- **Dos módulos con factor común** → `gcd(n1, n2)`; con eso se factorizan ambos.
- **`p` y `q` muy próximos** → Fermat (`n = a² − b²`), implementado en `RsaCtfTool` y en casi cualquier writeup.

## 4. Descifrar y comprobar

```python
m = pow(c, d, n)
print(m.to_bytes((m.bit_length() + 7)//8, 'big'))
```

Si el resultado no es texto, prueba `long_to_bytes` de `pycryptodome`, revisa endianness del `c` o si hay un padding (PKCS#1 v1.5) que haya que quitar.

## 5. Errores típicos

- **`ValueError: base is not invertible`** → `e` y φ no son coprimos; el reto usa otro exponente o hay que buscar `d` con Bezout.
- **`factorint` se cuelga** → `n` es grande; cambia de herramienta antes que de estrategia.
- **Texto basura tras descifrar** → `c` está en hex/bytes mal interpretado, o el mensaje va cifrado con otra clave.
- **`n` par** → factor trivial 2; comprueba que no estás leyendo la clave pública de otro reto.

## 6. Detección y mitigación (lado real)

- NIST SP 800-57: 2048 bits es el mínimo aceptable hasta 2030 y 3072 a partir de ahí; 1024 está deprecado (RSA-768 se factorizó en 2009).
- `e = 3` sin padding OAEP permite ataques de raíz; usa siempre OAEP.
- Rotar claves ante cualquier sospecha de factorización (módulos compartidos entre certificados).
- En CTF, documenta el ataque y la matemática; el valor está en reconocer el supuesto roto.

MITRE: T1553 (subversión de confianza), T1600 (debilidad criptográfica).
