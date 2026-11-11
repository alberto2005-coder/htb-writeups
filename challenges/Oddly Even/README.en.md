---
challenge: Oddly Even
category: Challenge
type: coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, parity, modulo, stdin-stdout]
---

# Oddly Even — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

The shortest challenge in the category: read a number and print `odd` or `even`. No binary, no service, no crypto trick, just a correct read of the input and a parity test that also handles zero and negatives.

## Statement and surface

- **Coding** category, **Very Easy** difficulty.
- The platform provides an editor (C, C++, Python or Rust) and the statement.
- Input: one integer.
- Output: `odd` if it is odd, `even` if it is even.

```text
Input
3

Output
odd
```

## Recon

Nothing to scan. Fix the contract first:

- The output is lowercase with no extra text.
- `0` is even.
- Negatives count too: in Python `-3 % 2` is `1`, so the check works without `abs()`.

## Code analysis

There is no prior code. The solution is one condition:

```python
n = int(input())
print("even" if n % 2 == 0 else "odd")
```

In C, `%` with negatives can return `-1`, so the correct odd test is `n % 2 != 0`, not `n % 2 == 1`.

## Root cause

No vulnerability. The only risk is printing extra text (`Odd`, `impar`, a trailing line) or using a comparison that fails on negatives in C/C++.

## Local reproduction

```bash
for n in 3 0 -3; do printf '%s\n' "$n" | python3 oddly_even.py; done
```

```python
# oddly_even.py
n = int(input())
print("even" if n % 2 == 0 else "odd")
```

## Exploitation

1. Read the integer.
2. Print `even` or `odd` in lowercase.
3. Submit; the platform validates the output and returns the flag.

## Evidence

- Local output for `3`, `0` and `-3`.
- No real flag in this writeup.

## Lessons learned

- Coding challenges test the input/output contract as much as the algorithm.
- Modulo behaviour with negatives differs between languages; test it.
- Printing the exact string (`odd`/`even`) avoids silly validation failures.

## Mitigations and detection

- Not applicable: there is no security component.
- As a habit, validate input ranges and output formats in any parser.

## References

- <https://www.hackthebox.com/challenges/oddly-even>
- <https://x3ric.com/blog/posts/HackTheBox-Oddly-Even-Challenge>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/oddly-even/>
- <https://motasem-notes.net/practical-coding-in-cyber-security-hackthebox-coding-challenges>
