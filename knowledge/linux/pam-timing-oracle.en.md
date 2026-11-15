---
title: PAM — timing oracle in a modified module
tags: [linux, pam, timing-attack, authentication, privesc]
---

# PAM — timing oracle in a modified module

[🇪🇸 Español](pam-timing-oracle.md) | **English**

## Concept

A PAM module that compares the password character by character and exits on the first mismatch leaks information through response time. If the module runs in `su` or `sshd`, a local attacker can recover root's password by measuring how long each attempt takes.

## When it applies

- A suspicious `.so` sits in `/lib/security` or `/usr/lib/security`.
- The ticket or code mentions a fixed-length password.
- `su` takes longer with correct prefixes.

## Procedure

1. Find PAM modules with anomalous dates or hashes.
2. Confirm the comparison is incremental (Ghidra/objdump).
3. Time `su` for each candidate and keep the slowest.
4. Repeat character by character and validate the full password.

```bash
for c in {a..z} {0..9}; do
  printf '%s' "$candidate$c" | timeout 1 su -c true root 2>/dev/null
  printf '%s %s\n' "$c" "$(date +%s%N)"
done
```

## Variants

- The module may compare hashes instead of text; the attack still works if the comparison is incremental.
- Use `perf stat` or `hyperfine` to reduce noise.
- If the module locks after several failures, space out the attempts.

## Limitations

- System noise can hide microsecond differences.
- The password must have a manageable alphabet and length.
- Local access is needed to invoke `su` repeatedly.

## Mitigation and detection

- Use constant-time comparisons (`CRYPTO_memcmp`).
- Verify PAM module integrity (`dpkg -V`, hashes).
- Rate-limit attempts and alert on repeated `su` patterns.
- Never store cleartext passwords in custom modules.

## References

- <https://www.man7.org/linux/man-pages/man8/pam.8.html>
- <https://www.man7.org/linux/man-pages/man3/pam_authenticate.3.html>
- <https://cwe.mitre.org/data/definitions/208.html>
