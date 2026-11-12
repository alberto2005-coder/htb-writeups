---
challenge: MetaVault
type: Blockchain
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, metadata, bytecode, sourcify, business-ctf]
---

# MetaVault — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A "MetaVault" contract hides a secret in its metadata. Fetch the bytecode, verify/decompile it with Sourcify and locate the embedded string; use it to call the emergency function and drain the vault.

## Prompt and surface

- Blockchain, Easy, retired (Business CTF 2024).
- RPC, address and a management interface are provided.
- The goal is to drain the contract funds.

## Reconnaissance

```bash
cast code <CONTRACT> --rpc-url <RPC>
cast call <CONTRACT> "owner()(address)" --rpc-url <RPC>
```

The bytecode includes Solidity metadata (`a264...`). Extract it and send it to a verifier/decompiler:

```text
https://playground.sourcify.dev/
```

## Analysis

1. Identify the metadata and compiler version.
2. Rebuild the interface and public functions.
3. Look for a string/constant in metadata or bytecode.
4. Locate the `emergency` or similar function that transfers the balance.
5. Call it with the secret and confirm the balance change.

```bash
cast send <CONTRACT> "emergency(string)" "<secret>" --rpc-url <RPC> --private-key <KEY>
cast balance <CONTRACT> --rpc-url <RPC>
```

## Root cause

Contract metadata leaks information and the privileged function is protected by a static secret. Anyone reading the bytecode can invoke it.

## Local reproduction

1. Deploy the contract on Anvil.
2. Extract the metadata.
3. Verify the code.
4. Call the function.
5. Check the balance is zero.

## Evidence

- Bytecode and metadata.
- Verified/decompiled code.
- Transaction and final balance.
- Redacted flag.

## Lessons learned

- Solidity metadata is public.
- A secret in bytecode is not a secret.
- Contract verification speeds up analysis.
- Emergency functions are critical targets.

## Mitigation and detection

- Never embed secrets in contracts.
- Use robust access control and multisig.
- Audit privileged functions.
- Monitor unexpected withdrawals.

## References

- <https://wepfen.github.io/writeups/metavault>
- <https://docs.sourcify.dev/>
- <https://book.getfoundry.sh/>
