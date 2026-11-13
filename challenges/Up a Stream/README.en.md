---
challenge: Up a Stream
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, java, streams, decompilation, encoding]
---

# Up a Stream — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A JAR transforms each character with Java streams, reverses the order, applies three arithmetic functions and repeats the result five times. Decompiling the bytecode allows inverting the operations and recovering the flag from `output.txt`.

## Prompt and surface

- Reversing, Easy, retired.
- `stream.jar` and `output.txt` are provided.
- The JAR prints an obfuscated string; the file contains the real flag's output.

```bash
file stream.jar output.txt
java -jar stream.jar
```

## Reconnaissance

- The JAR runs a `dunkTheFlag` function.
- It uses `chars()`, `mapToObj`, `reduce`, `peek` and `Collectors`.
- Output is separated by `O`, not zero.
- The result is repeated five times.

```bash
unzip -l stream.jar
```

## Code analysis

Decompile with CFR or `javap` and simplify the stream chain. `peek` calls do not change the value, so `hydrate` and `waterlog` do not participate in the final transformation.

Relevant functions:

```java
moisten(n) = n % 2 == 0 ? n : n * n
drench(n) = n << 1
dilute(n) = n / 2 + n
```

The first reduction reverses character order; the second concatenates and the final one appends `O` after each hex value.

## Root cause

There is no security flaw: this is a reversing exercise. Obfuscation relies on verbose streams and misleading function names, not cryptography.

## Local reproduction

1. Decompile the JAR.
2. Confirm local output matches `java -jar stream.jar`.
3. Take one of the five repetitions.
4. Split on `O`, convert from hex and apply the inverse functions.
5. Concatenate in reverse order.

```java
undilute(n) = n * 2 / 3
undrench(n) = n >> 1
unmoisten(n) = n % 2 == 0 ? n : (int) Math.sqrt(n)
```

```bash
java Solve.java "$(cat output.txt)"
```

## Evidence

- JAR output.
- Inverse functions and intermediate result.
- Redacted flag.

## Lessons learned

- `peek` does not transform the stream; it only observes.
- Function names do not describe their real effect.
- Repeating the output five times makes sampling easy.

## Mitigations and detection

- Do not use obfuscation to protect secrets.
- Verify JAR integrity before execution.
- Analyse bytecode in an isolated environment.
- For real secrets, use encryption and key management.

## References

- <https://www.hackthebox.com/challenges/Up%20a%20Stream>
- <https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html>
- <https://www.javadecompilers.com/>
