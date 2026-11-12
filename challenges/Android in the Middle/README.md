---
challenge: Android in the Middle
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, diffie-hellman, mitm, android, key-exchange]
---

# Android in the Middle — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Dos clientes intercambian claves Diffie-Hellman sin autenticar las claves públicas. Un atacante en el medio reemplaza `A` y `B` por sus propias claves, establece un secreto distinto con cada extremo y descifra/reenvía los mensajes.

## Enunciado y superficie

- Crypto, Very Easy, retirado.
- Se simula el canal entre dos clientes (Android/script).
- El servidor o intermediario ve las claves públicas.

## Reconocimiento

Se identifica el grupo y el generador:

```text
p = <PRIME>
g = <GENERATOR>
A = g^a mod p
B = g^b mod p
```

Si no hay firma ni verificación de identidad, el intercambio es vulnerable a MITM.

## Análisis

El atacante genera `x` e `y`, envía `g^x` a Alice y `g^y` a Bob. Calcula:

```text
K1 = A^x mod p   # con Alice
K2 = B^y mod p   # con Bob
```

Cada extremo cifra con una clave distinta; el atacante descifra con `K1`, vuelve a cifrar con `K2` y reenvía. El resultado es un canal transparente.

## Explicación del fallo

Diffie-Hellman sin autenticación no establece con quién se comparte la clave. Un intermediario puede sustituir las claves públicas y mantener dos sesiones independientes.

## Reproducción local

1. Interceptar `A` y `B`.
2. Generar claves propias y enviarlas.
3. Derivar `K1` y `K2`.
4. Descifrar con una y cifrar con la otra.

```python
K1 = pow(A, x, p)
K2 = pow(B, y, p)
```

## Evidencia

- Valores `p`, `g`, `A`, `B` redactados.
- Claves del atacante y secretos derivados (redactados).
- Mensaje descifrado con la flag redactada.

## Lecciones aprendidas

- DH sin autenticación es vulnerable a MITM.
- El tamaño del grupo no evita el problema de identidad.
- La firma de claves o TLS mitiga el ataque.
- Un “Android” en el medio puede ser un script, no una app.

## Mitigación y detección

- Autenticar claves con certificados o firmas.
- Usar TLS/Noise con identidad verificada.
- Fijar claves públicas cuando corresponda.
- Detectar retardos y renegociaciones anómalas.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/android-in-the-middle/>
- <https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange>
- <https://attack.mitre.org/techniques/T1557/>
