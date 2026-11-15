---
title: Hashcat — masks for formatted passwords
tags: [linux, hashcat, password-cracking, mask, sha256]
---

# Hashcat — masks for formatted passwords

[🇪🇸 Español](hashcat-mask-attack.md) | **English**

## Concept

A mask describes the password structure: fixed characters and variable positions. It is much faster than a dictionary when the format is known (for example, `susan_nasus_` followed by nine digits).

## When it applies

- There is a hash and a format hint (email, policy, ticket).
- The prefix or suffix is known.
- The search space fits in a reasonable time.

## Procedure

1. Identify the hash type with `hashid` or `hashcat --identify`.
2. Choose the mode (`-m`) and build the mask.
3. Compute the space: `?d` = 10, `?l` = 26, `?a` = 95.
4. Run with `-a 3` and, if needed, `--increment`.

```bash
hashcat hash.txt -m 1400 -a 3 'susan_nasus_?d?d?d?d?d?d?d?d?d'
hashcat hash.txt -m 1400 -a 3 -1 '?l?d' '?1?1?1?1?1?1'
```

## Variants

- `?u` uppercase, `?s` symbols, `?b` bytes.
- `--increment` tries increasing lengths.
- `-O` uses the optimized kernel if length permits.
- A dictionary with rules (`-r`) may be better when base words exist.

## Limitations

- The space grows exponentially; nine digits is 10^9.
- Speed depends on the GPU and mode.
- A wrong hint makes the search useless.

## Mitigation and detection

- Use long, random passwords, not predictable patterns.
- Store with Argon2id/bcrypt and a unique salt.
- Rate-limit attempts and monitor CPU/GPU spikes.
- Review policies that create common prefixes.

## References

- <https://hashcat.net/wiki/doku.php?id=mask_attack>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://hashcat.net/hashcat/>
