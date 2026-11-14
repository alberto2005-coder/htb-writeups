---
topic: Exposición parcial de clave RSA
tags: [crypto, rsa, partial-key, factorization, primes]
---

# RSA Partial Key Exposure

**English** | [🇪🇸 Español](rsa-partial-key.md)

## Concept

If bits of `p` or `q` leak, `n = p*q` allows the primes to be reconstructed. The search grows from the least significant bit and is pruned by congruence modulo `2^k`.

## When it applies

- Challenges provide `n`, `e`, `c` and a bit mask.
- Keys generated with insufficient entropy.
- Messages that reveal prime bits.

## Procedure

1. Align known bits from the LSB.
2. Try the four bit combinations for `p` and `q` at each position.
3. Keep only branches satisfying `p*q ≡ n (mod 2^k)`.
4. Verify `p*q == n` at the end.
5. Compute `d` and decrypt.

```python
if ((p + dp) * (q + dq)) % (1 << (k + 1)) == n % (1 << (k + 1)):
    # valid branch
    ...
```

## Variants

- Known bits from the MSB.
- Coppersmith when a small part is known.
- Parity or high-bit attacks.

## Limitations

- A sufficient fraction of bits is required.
- A misaligned mask breaks pruning.
- `p` and `q` must be valid primes.

## Mitigation

- Never expose bits or intermediate values.
- Rotate keys after a leak.
- Use generators with adequate entropy.

## Detection

- Keys with repeated structure.
- Published generation metadata.
- Challenges or APIs leaking bits.

## References

- <https://en.wikipedia.org/wiki/RSA_(cryptosystem)>
- <https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf>
- <https://attack.mitre.org/techniques/T1556/>
