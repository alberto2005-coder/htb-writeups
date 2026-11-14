---
topic: AES-CBC bit flipping
tags: [crypto, aes, cbc, bit-flipping, malleability, iv]
---

# AES-CBC bit flipping

**English** | [🇪🇸 Español](cbc-bit-flipping.md)

## Concept

In AES-CBC each plaintext block is XORed with the previous ciphertext block before encryption. If the attacker knows the plaintext and can modify the ciphertext, they change one byte in the previous block to alter the corresponding byte in the next block.

## When it applies

- CBC encryption without a MAC or AEAD.
- Cookies, tokens or parameters the client returns encrypted.
- Plaintext with known structure (`user=`, `role=`, `admin`).
- A controllable IV or first block.

## Procedure

1. Obtain a ciphertext and its plaintext.
2. Locate the target byte in block `P[i]`.
3. Compute `C[i-1]' = C[i-1] XOR P[i] XOR P[i]'`.
4. Send the modified ciphertext.
5. Accept that `P[i-1]` becomes corrupted.

```text
P[i] = D(C[i]) XOR C[i-1]
C[i-1]' = C[i-1] XOR P[i] XOR P[i]'
```

## Variants

- Modify the IV to change only `P[1]`.
- Turn `bdmin` into `admin` by flipping one byte.
- Alter a role or identifier in a token.
- Chain blocks to preserve structure.

## Limitations

- The block before the modified one is corrupted.
- The original plaintext must be known.
- PKCS#7 may fail if the last block is altered.
- A MAC or AEAD defeats the attack.

## Mitigation and detection

- Use AES-GCM or encrypt-then-MAC.
- Verify integrity before decryption.
- Do not accept client ciphertexts without authentication.
- Alert on padding failures and ciphertexts with anomalous lengths or bytes.

## References

- <https://owasp.org/www-community/attacks/CBC_bit_flipping>
- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://cwe.mitre.org/data/definitions/353.html>
- <https://attack.mitre.org/techniques/T1556/>
