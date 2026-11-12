---
challenge: I know Mag1k
type: Crypto
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [crypto, des, cbc, padding-oracle, web]
---

# I know Mag1k — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real cookie or flag.

## TL;DR

The session cookie is encrypted and the server returns 500 on invalid padding. The block size is 8 bytes, so this is DES-CBC with PKCS#7. A padding-oracle attack decrypts the cookie and then encrypts a JSON with `"role":"admin"` for escalation.

## Brief and surface

- Crypto/Web, Easy, retired.
- An application with login and an `iknowmag1k` cookie.
- The server responds differently for valid and invalid padding.

```bash
curl -i http://<IP>/profile.php
```

## Recon

The cookie is base64 and its length is not a multiple of 16, but is a multiple of 8. That rules out AES and points to DES-CBC.

```text
cookie = base64(IV || ciphertext)
block_size = 8
```

Adding 8 characters to the username produces 16 extra encrypted bytes.

## Source analysis

The server decrypts the cookie, strips PKCS#7 padding and shows the dashboard if the JSON is valid. Bad padding produces `500 Internal Server Error`; valid padding produces `200`. That difference is the oracle.

## The bug

CBC is malleable: changing the previous block controls the plaintext of the next block. The padding oracle recovers the decrypted value byte by byte and then reuses the primitive to encrypt arbitrary JSON.

## Local reproduction

Implement the oracle with `requests`:

```python
def oracle(cookie):
    r = requests.get(f'{url}/profile.php', cookies={
        'PHPSESSID': phpsessid,
        'iknowmag1k': cookie
    })
    return r.status_code != 500
```

For each block, try the last byte until padding `0x01` appears, compute the intermediate byte and repeat with `0x02`, `0x03`, etc.

## Exploitation

Decrypt the original cookie and build the target JSON:

```json
{"user":"<USER>","role":"admin"}
```

Encrypt it with the same primitive (the oracle also encrypts) and send it. The server shows the admin panel with the flag.

## Evidence

- 500/200 difference and 8-byte block size.
- Padding-oracle script with the cookie redacted.
- Admin panel with the flag redacted.

## Lessons learned

- Block size identifies the cipher.
- A distinct padding error is an oracle.
- CBC without authentication allows decryption and encryption.
- The same primitive forges the admin JSON.

## Mitigations and detection

- Use AEAD (AES-GCM, ChaCha20-Poly1305) and authenticate the cookie.
- Do not reveal padding errors; always respond the same.
- Sign the session server-side and never trust a client-side role.
- Detection: many requests with altered cookies and 500 responses.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/crypto/i-know-mag1k/>
- <https://owasp.org/www-community/attacks/Padding_Oracle_Attack>
- <https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#CBC>
