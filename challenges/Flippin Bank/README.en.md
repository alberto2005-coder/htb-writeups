---
challenge: Flippin Bank
type: Crypto
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [crypto, aes, cbc, bit-flipping, known-plaintext, length-extension]
---

# Flippin Bank — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The server encrypts `logged_username=<user>&password=<pass>` with AES-CBC and returns the ciphertext. If a submitted ciphertext decrypts to something containing `admin&password=<PASSWORD>`, it returns the flag. Flipping one byte of the first block changes the next plaintext block and turns `bdmin` into `admin`.

## Statement and surface

- Crypto, Medium, retired.
- The Python server source and a remote instance are provided.
- The server listens on 1337.

```bash
nc <IP> 1337
```

## Reconnaissance

The code shows:

- AES-CBC with a random key and IV per process.
- PKCS#7.
- A message built from the username and password.
- A check that forbids the substring `admin&password=<PASSWORD>` in the original message.

```python
msg = 'logged_username=' + user + '&password=' + passwd
assert 'admin&password=<PASSWORD>' not in msg
```

## Code analysis

The encryption is unauthenticated. In CBC, each plaintext block is XORed with the previous ciphertext block before encryption. Changing a byte in `C[i-1]` changes the corresponding byte in `P[i]` and corrupts `P[i-1]`.

```text
P1 = D(C1) XOR IV
P2 = D(C2) XOR C1
```

## Why it works

Choose username `bdmin` and a password starting with `g0ld3n_b0y`. The original message contains `bdmin&password=g...`, which does not match the forbidden string. Flipping the first byte of `C1` changes the first byte of `P2` from `b` to `a`, so the second block starts with `admin&password=g...`.

## Local reproduction

```bash
python3 -m venv venv
. venv/bin/activate
pip install pycryptodome pwntools
python server.py
```

- The local server uses a random key and IV.
- Test the script against localhost before the instance.

## Exploitation

```python
from pwn import remote

io = remote("<IP>", 1337)
io.sendlineafter(b"username: ", b"bdmin")
io.sendlineafter(b"password: ", b"g0ld3n_b0y")

io.recvuntil(b"Leaked ciphertext: ")
ct = bytearray.fromhex(io.recvline().decode())
ct[0] ^= ord("b") ^ ord("a")
io.sendlineafter(b"enter ciphertext: ", ct.hex().encode())
print(io.recvall().decode())
```

The response contains the flag; it is redacted.

## Evidence

- Original and modified ciphertext with the changed byte marked.
- Server output confirming the login.
- Redacted flag.

## Lessons learned

- CBC without a MAC is malleable.
- A controlled byte in the previous block changes the next block.
- Checks on the original plaintext do not protect the ciphertext.

## Mitigations and detection

- Use AES-GCM or encrypt-then-MAC with HMAC.
- Verify integrity before decryption and reject altered ciphertexts.
- Do not accept arbitrary client ciphertexts.
- Alert on padding failures, abnormal lengths and repeated decryption attempts.

## References

- <https://www.hackthebox.com/challenges/Flippin%20Bank>
- <https://csrc.nist.gov/publications/detail/sp/800-38a/final>
- <https://owasp.org/www-community/attacks/CBC_bit_flipping>
- <https://attack.mitre.org/techniques/T1556/>
