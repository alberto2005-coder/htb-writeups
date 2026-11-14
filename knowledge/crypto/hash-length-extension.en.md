---
topic: Hash length extension — SHA-256(secret || data)
tags: [crypto, hash, sha256, mac, length-extension]
---

# Hash length extension — SHA-256(secret || data)

**English** | [🌐 Español](hash-length-extension.md)

## Concept

A MAC built as `SHA-256(secret || data)` is vulnerable to hash length extension. Knowing the signature and the secret length, an attacker can compute a valid signature for `data || padding || extra` without knowing the secret. It does not work against HMAC, which is designed to prevent it.

## When it applies

- The application validates a checksum such as `hash(secret + email)` or `sha256(secret + parameter)`.
- A valid message and signature are known, and the secret length is bounded.
- The signed parameter is later used in a sensitive operation, such as command injection.

## Procedure

1. Identify the algorithm and confirm it is `secret || data`, not HMAC.
2. Try secret lengths and generate candidates with `hash_extender`.
3. Send the message with padding bytes and the new signature.
4. Detect the correct length from the response and append the final payload.

## Commands

```bash
hash_extender --data "user@example.com" -s "<SIGNATURE>" --append "@$(id)" --secret-min=1 --secret-max=80 --out-data-format=html > candidates
# Send each candidate preserving the bytes and the new signature
```

## Variants

- Apply the same principle to SHA-1 and MD5.
- Use a secret length leaked by an error or by the identifier size.
- Combine it with command injection in the concatenated field.

## Limitations

- It does not work against HMAC or per-message random salts.
- The secret length must be known or brute-forceable.
- The transport must preserve null bytes and not truncate the message.

## Mitigation

- Use HMAC-SHA-256 with constant-time comparison.
- Do not build a MAC by concatenating a secret with user input.
- Limit and normalize the signed field before using it.

## Detection

- Valid signatures for messages with padding or non-printable bytes.
- Parameters that grow after a separator while keeping an old checksum.
- Validation errors across variable secret lengths.

## References

- [0xdf — Extension](https://0xdf.gitlab.io/2023/03/18/htb-extension.html)
- [Length extension attack](https://en.wikipedia.org/wiki/Length_extension_attack)
- [CWE-328 — Use of Weak Hash](https://cwe.mitre.org/data/definitions/328.html)
