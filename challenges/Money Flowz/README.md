---
challenge: Money Flowz
type: OSINT
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [osint, reddit, ethereum, ropsten, blockchain, transaction]
---

# Money Flowz — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La descripción da un nombre, “Frank Vitalik”. Buscando en redes se llega a un perfil de Reddit y a una estafa con un monedero Ethereum en la testnet Ropsten. La flag está en el `input data` de una transacción saliente.

## Enunciado y superficie

- OSINT, Medium, retirado.
- Solo hay una descripción y un nombre.
- No hay archivos ni instancia.

```text
Frank Vitalik is a hustler, can you figure out where the money flows?
```

## Reconocimiento

Se buscan variantes del nombre y perfiles públicos:

```text
"Frank Vitalik" reddit
"Frank Vitalik" ethereum
"Frank Vitalik" free coinz
```

Se localiza un post de Reddit y una publicación en Steemit que promociona “free coinz” y comparte una dirección de monedero.

## Análisis

1. Se identifica la dirección y la red (Ropsten, testnet de Ethereum).
2. Se consulta el explorador de bloques y se filtran transacciones salientes (`OUT`).
3. Se revisan los detalles de cada salida y el campo `Input Data`.
4. Se cambia la visualización de hex a UTF-8.
5. El texto contiene la flag, que se redacta.

```text
# Ropsten está deprecada; usar el archivo web o un explorador histórico
https://ropsten.etherscan.io/address/<address>
```

## Explicación del fallo

La información se publica voluntariamente en redes y en la blockchain. La pseudonimia no impide correlacionar identidad, monedero y transacciones.

## Reproducción local

1. Repetir las búsquedas del nombre.
2. Documentar el pivote Reddit → Steemit → monedero.
3. Consultar las transacciones salientes.
4. Decodificar el input en UTF-8.
5. Guardar capturas con la flag redactada.

## Evidencia

- Capturas de los perfiles y del post.
- Dirección y transacción (redactadas).
- Decodificación del input.
- Flag redactada.

## Lecciones aprendidas

- Un nombre y una red social bastan para iniciar un pivote.
- La blockchain es un registro público permanente.
- El `input data` puede transportar mensajes.
- Las testnets desaparecen; conviene archivar evidencias.

## Mitigación y detección

- No publicar direcciones vinculadas a identidad real.
- Evitar mensajes en transacciones.
- Usar monederos separados por contexto.
- Formar en huella digital y OSINT.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/money-flowz/>
- <https://ethereum.org/>
- <https://en.wikipedia.org/wiki/Open-source_intelligence>
