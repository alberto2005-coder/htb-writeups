---
topic: CBC padding oracle
tags: [crypto, cbc, pkcs7, padding-oracle, aes, des]
---

# CBC padding oracle

**English** | [🇪🇸 Español](padding-oracle.md)

## Concept

In CBC, each plaintext block is XORed with the previous ciphertext block. If the server reveals whether PKCS#7 padding is valid, an attacker can modify the previous block and observe the response to recover plaintext byte by byte. The same primitive can encrypt an arbitrary message.

## When it applies

- CBC encryption with PKCS#7 and no authentication (no MAC/AEAD).
- The server distinguishes invalid padding from invalid data (code, message or timing).
- The attacker controls the IV and ciphertext (cookie, token, parameter).
- The block size is known (8 for DES/3DES, 16 for AES).

## Requirements and conditions

1. Accessible ciphertext and IV.
2. Observable oracle (200 vs 500, redirect, timing).
3. Ability to send many values without blocking.
4. Standard PKCS#7 padding.

## Procedure

For the last block, flip the penultimate byte until padding is `0x01`. The intermediate byte is `b ^ 0x01`; plaintext is `prev_block[-1] ^ intermediate`. Repeat with `0x02`, `0x03`, etc.

```python
def oracle(cookie):
    r = requests.get(url, cookies={'session': cookie})
    return r.status_code != 500
```

```python
for b in range(256):
    forged = prev[:-1] + bytes([b])
    if oracle(base64.b64encode(forged + ct)):
        inter = b ^ 0x01
        plain = prev[-1] ^ inter
        break
```

To encrypt, choose the target block and compute the previous block as `D(C) ^ P`.

## Variants

- **POODLE**: padding oracle in SSL 3.0 with CBC.
- **Lucky13**: timing difference in TLS CBC.
- **Cookie/token**: the oracle is a session cookie or encrypted token.
- **Padding oracle + bit flipping**: without an oracle, modifying the IV may be enough.

## Limitations

- AEAD (AES-GCM, ChaCha20-Poly1305) is not vulnerable to this attack.
- A MAC or signature over the ciphertext blocks it.
- WAFs and rate limiting hinder exploitation.
- Padding may differ from PKCS#7 (ZeroPadding, ISO 10126).

## Mitigation

- Use AEAD and authenticate the ciphertext.
- Do not reveal padding errors; always respond the same.
- Sign cookies/tokens server-side.
- Rotate keys if exploitation is detected.

## Detection

- Bursts of requests with altered cookies and 500 responses.
- Timing differences between valid and invalid padding.
- Increased 400/500 errors on endpoints with encrypted tokens.
- WAF: rules for repeatedly altered base64 payloads.

MITRE ATT&CK: T1552 (Unsecured Credentials), T1140 (Deobfuscate/Decode Files or Information).

## References

- <https://owasp.org/www-community/attacks/Padding_Oracle_Attack>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC>
- <https://www.openssl.org/docs/man3.0/man7/EVP_CIPHER-AES.html>
