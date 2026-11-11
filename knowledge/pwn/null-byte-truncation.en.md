---
title: "C strings and null bytes: silent truncation"
tags: [pwn, c-strings, strcpy, null-byte, crypto, logic-bug]
---

# C strings and null bytes: silent truncation

**English** | [🇪🇸 Español](null-byte-truncation.md)

## 1. When to look here

Keys, tokens or binary blobs are copied with `strcpy`, `strlen`, `strcmp` or `%s`. These functions stop at the first `\0`, so random data containing a null is cut without warning.

## 2. The rule

A C string ends at the first zero byte:

```c
char buf[8] = { 'A', 'B', '\0', 'C', 'D', 'E', 'F', 'G' };
strlen(buf);   // 2, not 8
strcpy(dst, buf);  // copies "AB" and the terminator
```

The rest stays in memory, but no string function sees it. If the buffer is reused, the bytes after the terminator are from the previous operation.

## 3. Where the bug shows up

- **Keys from `/dev/urandom`**: any byte can be `\0`; the real key is shorter than requested.
- **Base64 tokens**: decoded to bytes, an internal null truncates when copied.
- **Uninitialised buffers**: `strcpy` copies the terminator and leaves garbage behind, which a later read may interpret.
- **Comparisons**: `strcmp` treats two strings as equal if they match only up to the first null.

## 4. The vault case

A program generates a key of length `n` (0–31) and copies it to a global with `strcpy`. The loop avoids nulls at position `i`, but not earlier. Reducing `n` from 31 to 0 moves the terminator to the start and the global becomes empty. XOR with zero returns the original text.

```text
n=31: [ k0 k1 ... k30 00 ]
n=2:  [ k0 k1 00 ]
n=0:  [ 00 ]
```

There is no corruption: the program does exactly what the string functions say.

## 5. How to spot it

- Review every `strcpy`/`strlen` that receives binary data.
- Check whether the length is stored separately; if not, the data is not a string.
- Look for `memset` covering only part of the buffer and leaving old bytes.
- During exploitation, try decreasing lengths and watch whether the secret changes size.

## 6. Mitigation

- Use `memcpy`/`memcmp` with explicit lengths and store `(buffer, length)`.
- Initialise the whole destination before copying (`memset(dst, 0, sizeof dst)`).
- Do not use `strcpy` with data that may contain `\0`; `strncpy` is not the fix either (it may omit the terminator).
- For keys, use a struct with a size or a type that does not rely on terminators.
- CWE-170 (improper null termination), CWE-327 (broken crypto).

## 7. Production detection

- Keys of variable or shorter-than-expected length in logs.
- Authentication failures that disappear when a token length changes.
- Differences between the declared size and `strlen` of the value.

References: `man 3 strcpy`, `man 3 strlen`, CWE-170 and the `memcpy` documentation.
