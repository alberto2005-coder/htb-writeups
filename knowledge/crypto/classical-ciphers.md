---
topic: Cifrados clásicos — Vigenère y análisis de frecuencia
tags: [crypto, vigenere, substitution, frequency-analysis]
---

# Cifrados clásicos — Vigenère y análisis de frecuencia

[🌐 English](classical-ciphers.en.md) | **Español**

## Concepto

Los cifrados clásicos no resisten el análisis de frecuencia ni el conocimiento del formato. En Vigenère se estima la longitud de la clave con Kasiski o el índice de coincidencia, se separa el texto en columnas y se resuelve cada César.

## Cuándo aplica

- Retos con texto cifrado alfabético.
- Contraseñas o notas ofuscadas con Vigenère.
- Claves cortas o texto plano predecible.

## Procedimiento

1. Identificar el alfabeto y eliminar separadores.
2. Estimar la longitud de clave con Kasiski o IC.
3. Separar el texto en columnas.
4. Resolver cada columna como un César.
5. Probar la clave y validar el texto plano.

## Comandos

```python
from collections import Counter
c = '...'
for shift in range(26):
    p = ''.join(chr((ord(x)-65-shift) % 26 + 65) for x in c)
    print(shift, p[:60])
```

## Variantes

- Sustitución monoalfabética con análisis de frecuencia.
- César con desplazamiento conocido.
- XOR de un byte y criba de texto plano.

## Limitaciones

- Las claves largas y el texto corto dificultan el ataque.
- Los alfabetos mixtos complican el análisis.
- Puede requerir idioma o formato conocido.

## Mitigación

- Usar criptografía moderna autenticada.
- No emplear cifrados clásicos para secretos.
- Rotar claves y no reutilizarlas.

## Detección

- Texto con distribución de letras anómala.
- Cadenas que parecen claves o alfabetos desplazados.

## Referencias

- <https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher>
- <https://attack.mitre.org/techniques/T1140/>
