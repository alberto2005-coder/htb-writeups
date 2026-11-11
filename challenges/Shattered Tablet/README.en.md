---
challenge: Shattered Tablet
category: Reversing
type: Reversing
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, ghidra, static, comparisons]
---

# Shattered Tablet — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A 64-bit ELF asks for a 40-character string and validates it with **40 independent comparisons**, one per index: `data[0] == 'H'`, `data[1] == 'T'` and so on. The condition order is deliberately shuffled, but each one pins a position. Retyping the buffer as `char[64]` in Ghidra (or using `pdf @ main` in radare2) lets you rebuild the string by sorting on the index.

## Brief and surface

- Reversing, Very Easy; Cyber Apocalypse 2023 challenge.
- A single binary, `tablet`, with no source.
- The story is a stone tablet shattered into pieces: each piece is one condition.

## Recon

```bash
file tablet
./tablet
```

`file` reports a 64-bit LSB PIE x86-64 ELF, dynamically linked and not stripped. Running it prints `Hmmmm... I think the tablet says: ` and reads up to 64 bytes from `stdin`; then it answers `Yes! That's right!` or `No... not that`.

## Source analysis

Ghidra shows a `main` with eight 8-byte variables (`local_48` to `local_10`) zeroed and a `fgets(data, 0x40, stdin)`. The check is a chain of `&&` over individual bytes:

```c
if ((data[34] == '4') && (data[20] == '3') && (data[36] == 'r') &&
    (data[1] == 'T') && (data[21] == 'v') && (data[6] == '0') && ...
```

The decompiler prints `local_28._2_1_`, `local_38._4_1_` and friends because it treats the buffer as eight `undefined8` values. Retype `local_48` as `char[64]`, rename it to `data`, and the conditions become readable and index-ordered.

## The bug

There is no cryptography and no real obfuscation: the expected string is **encoded as 40 comparisons**. Each character is checked on its own, so knowing the index and the literal is enough. The only work is translating Ghidra's offsets (`local_28._2_1_`) into `data[34]`.

## Local reproduction

```bash
chmod +x tablet
./tablet
# type 40 characters and read the verdict
```

The comparison can also be patched to print the buffer, but that is unnecessary: static analysis already yields every character.

## Exploitation

1. Open `tablet` in Ghidra and find `main`.
2. Retype `local_48` as `char[64]`; conditions become `data[i] == 'x'`.
3. Copy the `(i, 'x')` pairs and sort by index:

```python
pairs = [(34, '4'), (20, '3'), (36, 'r'), (1, 'T'), (21, 'v'), (6, '0'), (39, '}')]
buf = ['?'] * 40
for i, c in pairs:
    buf[i] = c
print(''.join(buf))
```

The full list has 40 pairs; with all of them, `''.join(buf)` is the flag. Without a decompiler: `radare2 -AA ./tablet`, `pdf @ main`, and a regular expression over the comparisons.

## Evidence

- `tablet`, a 64-bit PIE ELF, not stripped.
- 40 `data[i] == literal` conditions in `main`; the rebuilt string is kept in `private/`.

## Lessons learned

- **Buffer type**: without retyping to `char[64]`, Ghidra shows offsets and the order is lost.
- **Condition order is not flag order**: sort by index, not by appearance.
- **Length**: `fgets` accepts 64 bytes but only 40 are checked; no padding needed.

## Mitigations and detection

- Comparing the whole string with `strcmp` does not protect it better, but it stops leaking each character's position.
- If a secret must live client-side, derive it per user and verify server-side; any embedded literal can be extracted.
- Detection: binaries with dozens of consecutive byte comparisons against constants, typical of generated checkers.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/shattered-tablet/>
- <https://bryanmcnulty.com/posts/htb-shattered-tablet>
- <https://ghidra-sre.org/>
