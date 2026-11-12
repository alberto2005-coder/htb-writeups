---
topic: "Contratos inteligentes: estado, pagos y superficies típicas"
tags: [blockchain, solidity, evm, smart-contract, foundry]
---

# Contratos inteligentes: estado, pagos y superficies típicas

[🇬🇧 English](smart-contracts.en.md) | **Español**

## Idea

Un contrato es código inmutable con estado público y funciones que cualquiera puede llamar salvo que se restrinjan. La mayoría de los fallos no son de EVM sino de lógica: funciones sin control de acceso, pagos basados en estado manipulable, validaciones que faltan y `delegatecall` a código ajeno.

## Cuándo aplica

- Retos y auditorías de contratos con `Setup.sol` (qué cuenta como resuelto) y el contrato objetivo.
- Contratos con `payable`, `transfer`, `selfdestruct` o `delegatecall`.
- Instancias con RPC y clave privada del jugador.

## Lectura rápida

1. `Setup.sol`: dirección del objetivo, saldo inicial y condición de victoria.
2. Funciones `external`/`public` sin `onlyOwner` ni `require`.
3. Estado que el usuario puede cambiar y que decide un pago.
4. Bucles y llamadas externas antes de actualizar estado (reentrancy).
5. `delegatecall` y `selfdestruct` con destino controlable.

## Herramientas

```bash
cast call <CONTRATO> "lifePoints()(uint256)" --rpc-url <RPC>
cast send <CONTRATO> "funcion(uint256)" <ARG> --rpc-url <RPC> --private-key <PK>
cast balance <CONTRATO> --rpc-url <RPC>
forge test -vvv
```

```solidity
// lectura del almacenamiento sin función getter
vm.load(address(contract), bytes32(uint256(0)));
```

## Fallos típicos

- **Pago sin control**: `loot()` que transfiere si el estado llega a un valor que el atacante puede fijar.
- **Falta de validación**: restas sin comprobar límites, `uint` que envuelve (en versiones <0.8 o con `unchecked`), divisiones por cero.
- **Control de acceso ausente**: `initialize()` o `setOwner()` sin protección.
- **Reentrancy**: `call{value:}` antes de poner el saldo a cero.
- **Oráculos manipulables**: precio leído de un pool que el atacante mueve.
- **`delegatecall` a dirección del usuario**: ejecución en el contexto del contrato.

## Blindaje

- `require` de límites y de estado; eventos en cada cambio relevante.
- Patrón checks-effects-interactions y retirada por pull.
- `Ownable`/`AccessControl` en funciones administrativas.
- Pruebas con Foundry: fuzzing y escenarios de ataque.
- Revisión externa y límites de retirada.

## Detección

- Llamadas repetidas a la misma función en un bloque.
- Transferencias que vacían el saldo a una dirección nueva.
- Eventos con valores fuera de rango o cambios de estado sin evento.
- En monitoreo: alertas por `delegatecall`, `selfdestruct` y `owner` cambiado.

## Referencias

- <https://docs.soliditylang.org/en/latest/security-considerations.html>
- <https://swcregistry.io/>
- <https://book.getfoundry.sh/>
