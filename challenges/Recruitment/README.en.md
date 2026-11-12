---
challenge: Recruitment
type: Blockchain
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, ethereum, smart-contract, rpc, foundry, business-ctf]
---

# Recruitment — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

Introductory blockchain challenge: connect to the RPC, inspect the contract and send a transaction satisfying the `require` constraints. Once the check passes, the service returns the flag.

## Prompt and surface

- Blockchain, Very Easy, retired (Business CTF 2024).
- RPC, contract address and a management interface are provided.
- The goal is to satisfy the contract conditions.

## Reconnaissance

```bash
nc <IP> <PORT>
cast block-number --rpc-url <RPC>
cast code <CONTRACT> --rpc-url <RPC>
```

Review public functions and events. If source is available, read the `require` and initial state.

## Analysis

1. Identify the validating function.
2. Review types (`uint`, `address`, `string`) and bounds.
3. Compute the required value/argument.
4. Simulate with `cast call` before sending.
5. Send the transaction and query the state.

```bash
cast call <CONTRACT> "<function>(<args>)" <args> --rpc-url <RPC>
cast send <CONTRACT> "<function>(<args>)" <args> --private-key <KEY> --rpc-url <RPC>
```

## Root cause

The contract trusts a simple condition the attacker can satisfy. There is no access control or secure randomness; state is public and manipulable.

## Local reproduction

1. Start Anvil.
2. Deploy the contract with Foundry.
3. Repeat the call.
4. Verify the state change.
5. Request the flag from the service.

## Evidence

- `cast code`/`cast call` output.
- Transaction and receipt.
- Final state.
- Redacted flag.

## Lessons learned

- Contracts are public state machines.
- `require` is the logic gate to pass.
- Simulating before sending avoids wasted gas.
- Foundry/`cast` speeds up interaction.

## Mitigation and detection

- Do not use trivial conditions as authorisation.
- Apply access control and signatures.
- Review logic with tests and fuzzing.
- Monitor anomalous transactions.

## References

- <https://book.getfoundry.sh/>
- <https://www.hackthebox.com/>
- <https://ethereum.org/en/developers/docs/smart-contracts/security/>
