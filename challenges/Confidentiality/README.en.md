---
challenge: Confidentiality
type: Blockchain
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [blockchain, ethereum, erc721, ecdsa, signature-malleability]
---

# Confidentiality — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An ERC-721 contract guards a sensitive function with an ECDSA signature. The signature is not strictly bound to the signer and is malleable: replacing `s` with `n - s` and adjusting `v` yields another valid signature for the same message, enabling the privileged action.

## Brief and surface

- Blockchain, Medium, retired.
- Contract and a node/RPC are provided.
- The goal is to reach the protected function or claim the NFT.

## Recon

Review contract functions and `ecrecover` usage:

```solidity
function claim(bytes32 hash, uint8 v, bytes32 r, bytes32 s) external {
    require(ecrecover(hash, v, r, s) == owner);
    ...
}
```

If `s` format is not validated and EIP-712 with a domain is absent, the signature can be mutated.

## Analysis

ECDSA requires `s <= n/2` to avoid malleability. If the contract accepts any `s`, compute:

```text
s' = n - s
v' = 27 if v == 28, and vice versa
```

`(v', r, s')` remains valid for the same hash. Send it to the protected function to gain the privilege.

## The bug

The contract trusts `ecrecover` without checking `s` canonicality or binding the signature to a nonce/domain. Malleability lets an observed on-chain signature be reused.

## Local reproduction

1. Obtain a valid signature from the transaction or backend.
2. Compute `s' = n - s` with the curve order.
3. Adjust `v`.
4. Send the call with `cast` or ethers.

```bash
cast send <CONTRACT> "claim(bytes32,uint8,bytes32,bytes32)" <HASH> <V> <R> <S>
```

## Evidence

- Contract and vulnerable function.
- Original and malleated signatures (redacted).
- Transaction and event with the flag redacted.

## Lessons learned

- ECDSA is malleable if `s` is not normalised.
- `ecrecover` alone does not validate the signer.
- EIP-712 and nonces bind a signature to context.
- On-chain signatures are reusable without protection.

## Mitigation and detection

- Use OpenZeppelin `ECDSA` with canonical `s`.
- Implement EIP-712 with domain and nonce.
- Verify `v` in {27,28} and reject high `s`.
- Audit contracts using `ecrecover`.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/blockchain/confidentiality/>
- <https://eips.ethereum.org/EIPS/eip-712>
- <https://docs.openzeppelin.com/contracts/4.x/api/utils#ECDSA>
