---
topic: ASLR brute force
tags: [privesc, aslr, ret2libc, 32-bit, buffer-overflow]
---

# ASLR brute force

[🌐 Español](aslr-brute-force.md) | **English**

## Concept

On 32-bit binaries, ASLR entropy can be low: the libc base changes by only a few hundred positions. If the process can be restarted safely, a ret2libc loop hits the address with enough probability.

## When it applies

- 32-bit SUID without PIE and with NX.
- ASLR enabled but with `randomize_va_space=2` and a small range.
- A process that does not block retries or log failures.

## Procedure

1. Confirm NX, no canary and no PIE.
2. Measure the libc base range with `ldd`.
3. Compute `system`, `exit` and `/bin/sh` offsets.
4. Repeat the payload until a shell appears.

```bash
for i in $(seq 1 2000); do
  /usr/local/bin/ovrflw "$(python -c 'print "A"*112 + "<system>" + "<exit>" + "<binsh>"')" && break
done
```

## Variants

- Brute-forcing the return address on 32-bit.
- `ret2plt` when libc cannot be leaked.
- Canary brute force against a `fork()` server.

## Limitations

- Probability grows slowly with high entropy.
- The service must restart or accept many connections.
- Crashes may alert or stop the process.

## Mitigation and detection

- Build with PIE and canary.
- Use 64-bit ASLR and random `mmap`.
- Limit retries and monitor crashes.
- Alert on repeated SUID runs with oversized payloads.

## References

- <https://www.exploit-db.com/docs/english/28553-linux-classic-return-to-libc-&-return-to-libc-chaining-tutorial.pdf>
- <https://attack.mitre.org/techniques/T1068/>
