---
challenge: Android in the Middle
type: Crypto
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [crypto, diffie-hellman, mitm, android, key-exchange]
---

# Android in the Middle — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

Two clients exchange Diffie-Hellman keys without authenticating the public values. A man in the middle replaces `A` and `B` with its own keys, establishes a separate secret with each side and decrypts/forwards messages.

## Brief and surface

- Crypto, Very Easy, retired.
- A channel between two clients (Android/script) is simulated.
- The server or intermediary sees the public keys.

## Recon

Identify the group and generator:

```text
p = <PRIME>
g = <GENERATOR>
A = g^a mod p
B = g^b mod p
```

Without a signature or identity verification, the exchange is MITM-vulnerable.

## Analysis

The attacker generates `x` and `y`, sends `g^x` to Alice and `g^y` to Bob. It computes:

```text
K1 = A^x mod p   # with Alice
K2 = B^y mod p   # with Bob
```

Each side encrypts with a different key; the attacker decrypts with `K1`, re-encrypts with `K2` and forwards. The result is a transparent channel.

## The bug

Unauthenticated Diffie-Hellman does not establish who the key is shared with. An intermediary can substitute public keys and keep two independent sessions.

## Local reproduction

1. Intercept `A` and `B`.
2. Generate own keys and send them.
3. Derive `K1` and `K2`.
4. Decrypt with one and encrypt with the other.

```python
K1 = pow(A, x, p)
K2 = pow(B, y, p)
```

## Evidence

- `p`, `g`, `A`, `B` values redacted.
- Attacker keys and derived secrets (redacted).
- Decrypted message with the flag redacted.

## Lessons learned

- Unauthenticated DH is MITM-vulnerable.
- Group size does not solve identity.
- Key signatures or TLS mitigate the attack.
- The “Android” in the middle can be a script, not an app.

## Mitigation and detection

- Authenticate keys with certificates or signatures.
- Use TLS/Noise with verified identity.
- Pin public keys where appropriate.
- Detect unusual delays and renegotiations.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/android-in-the-middle/>
- <https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange>
- <https://attack.mitre.org/techniques/T1557/>
