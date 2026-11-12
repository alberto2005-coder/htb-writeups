---
challenge: Confidentiality
type: Blockchain
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [blockchain, ethereum, erc721, ecdsa, signature-malleability]
---

# Confidentiality — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un contrato ERC-721 protege una función sensible con una firma ECDSA. La firma no está vinculada de forma estricta al emisor y permite maleabilidad: cambiando `s` por `n - s` y ajustando `v` se obtiene otra firma válida para el mismo mensaje, lo que permite ejecutar la acción privilegiada.

## Enunciado y superficie

- Blockchain, Medium, retirado.
- Se entregan el contrato y un nodo/RPC.
- El objetivo es acceder a la función protegida o reclamar el NFT.

## Reconocimiento

Se revisan las funciones del contrato y el uso de `ecrecover`:

```solidity
function claim(bytes32 hash, uint8 v, bytes32 r, bytes32 s) external {
    require(ecrecover(hash, v, r, s) == owner);
    ...
}
```

Si no se valida el formato de `s` ni se usa `EIP-712` con dominio, la firma puede mutarse.

## Análisis

ECDSA exige `s <= n/2` para evitar maleabilidad. Si el contrato acepta cualquier `s`, se puede calcular:

```text
s' = n - s
v' = 27 si v == 28, y viceversa
```

La firma `(v', r, s')` sigue siendo válida para el mismo hash. Se envía a la función protegida y se obtiene el privilegio.

## Explicación del fallo

El contrato confía en `ecrecover` sin comprobar la canonicalidad de `s` ni vincular la firma a un nonce/dominio. La maleabilidad permite reutilizar una firma observada en la cadena.

## Reproducción local

1. Obtener una firma válida de la transacción o del backend.
2. Calcular `s' = n - s` con el orden de la curva.
3. Ajustar `v`.
4. Enviar la llamada con `cast` o ethers.

```bash
cast send <CONTRACT> "claim(bytes32,uint8,bytes32,bytes32)" <HASH> <V> <R> <S>
```

## Evidencia

- Contrato y función vulnerable.
- Firma original y firma maleada (redactadas).
- Transacción y evento con el flag redactado.

## Lecciones aprendidas

- ECDSA es maleable si no se normaliza `s`.
- `ecrecover` no valida el emisor por sí solo.
- EIP-712 y nonces vinculan la firma al contexto.
- Las firmas observadas en cadena son reutilizables si no hay protección.

## Mitigación y detección

- Usar OpenZeppelin `ECDSA` con `s` canónico.
- Implementar EIP-712 con dominio y nonce.
- Verificar `v` en {27,28} y rechazar `s` alto.
- Auditar contratos que usan `ecrecover`.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/blockchain/confidentiality/>
- <https://eips.ethereum.org/EIPS/eip-712>
- <https://docs.openzeppelin.com/contracts/4.x/api/utils#ECDSA>
