---
topic: Multisig thresholds
tags: [blockchain, solidity, multisig, access-control, signatures]
---

# Multisig thresholds

**English** | [🇪🇸 Español](multisig-thresholds.md)

## Concept

A multisig wallet requires a minimum number of signers to authorise an action. The threshold must be checked explicitly, and signatures must be bound to the operation, chain and contract. A loop over signatures does not implement a threshold by itself.

## When it applies

- Treasuries and crowdfunding contracts.
- Protocol governance and upgrades.
- Withdrawals or closures controlled by a council.
- Any function accepting an array of signatures.

## Requirements and conditions

- List of authorised signers.
- Canonical message including operation, recipient, chain and nonce.
- ECDSA or equivalent verification.
- Duplicate-signer and minimum-count checks.

## Procedure

1. Define the `M`-of-`N` threshold.
2. Build the hash of the full operation.
3. Verify each signature and recover the signer.
4. Reject unknown and repeated signers.
5. Require `signatures.length >= M` before execution.
6. Execute only when the threshold is met.

```solidity
require(signatures.length >= threshold, "Not enough signatures");
require(uniqueSigners == threshold, "Invalid signers");
```

## Variants

- On-chain multisig with an owner list.
- Off-chain signatures verified by the contract.
- Threshold signatures (for example Schnorr or MPC).
- Timelock plus multisig for critical operations.

## Limitations

- An empty array can skip the loop if length is not checked.
- Signatures can be replayed without a nonce.
- The recipient and contract must be part of the signed message.
- Owner changes need their own access control.

## Mitigation

- Validate the threshold explicitly and separately from the loop.
- Include `address(this)`, `chainId` and a nonce in the hash.
- Normalise ECDSA signatures and reject non-canonical values.
- Avoid `selfdestruct` in business logic.
- Add a timelock and invariant tests.

## Detection

- Alert on empty arrays or fewer signatures than the threshold.
- Monitor owner and threshold changes.
- Review operations with unexpected recipients.
- Compare signature count with unique signer count.

## References

- <https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#ECDSA>
- <https://swcregistry.io/docs/SWC-105>
- <https://attack.mitre.org/techniques/T1548/>
