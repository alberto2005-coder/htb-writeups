---
topic: Contratos inteligentes: estado, pagos y superficies típicas
tags: [blockchain, solidity, evm, smart-contract, foundry]
---

# Smart contracts: state, payments and typical surface

**English** | [🇪🇸 Español](smart-contracts.md)

## Idea

A contract is immutable code with public state and functions anyone can call unless restricted. Most bugs are not EVM-level but logic-level: functions without access control, payouts based on manipulable state, missing validations and `delegatecall` into foreign code.

## When it applies

- Contract challenges and audits with a `Setup.sol` (what counts as solved) and a target contract.
- Contracts using `payable`, `transfer`, `selfdestruct` or `delegatecall`.
- Instances with RPC and a player private key.

## Quick reading

1. `Setup.sol`: target address, initial balance and win condition.
2. `external`/`public` functions without `onlyOwner` or `require`.
3. State the user can change that decides a payout.
4. Loops and external calls before state updates (reentrancy).
5. `delegatecall` and `selfdestruct` with a controllable target.

## Tooling

```bash
cast call <CONTRACT> "lifePoints()(uint256)" --rpc-url <RPC>
cast send <CONTRACT> "function(uint256)" <ARG> --rpc-url <RPC> --private-key <PK>
cast balance <CONTRACT> --rpc-url <RPC>
forge test -vvv
```

```solidity
// read storage without a getter
vm.load(address(contract), bytes32(uint256(0)));
```

## Typical flaws

- **Unprotected payout**: `loot()` transferring when state reaches a value the attacker can set.
- **Missing validation**: subtraction without bounds, wrapping `uint`, division by zero.
- **Missing access control**: `initialize()` or `setOwner()` left open.
- **Reentrancy**: `call{value:}` before zeroing the balance.
- **Manipulable oracles**: price read from a pool the attacker moves.
- **`delegatecall` to a user-supplied address**: code runs in the contract's context.

## Hardening

- `require` bounds and state; events on every relevant change.
- Checks-effects-interactions and pull-payment patterns.
- `Ownable`/`AccessControl` on administrative functions.
- Foundry tests: fuzzing and attack scenarios.
- External review and withdrawal limits.

## Detection

- Repeated calls to the same function in one block.
- Transfers draining the balance to a fresh address.
- Events with out-of-range values or state changes without an event.
- Monitoring alerts for `delegatecall`, `selfdestruct` and `owner` changes.

## References

- <https://docs.soliditylang.org/en/latest/security-considerations.html>
- <https://swcregistry.io/>
- <https://book.getfoundry.sh/>
