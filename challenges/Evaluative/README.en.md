---
challenge: Evaluative
category: Challenge
type: coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, polynomial, horner, stdin-stdout]
---

# Evaluative — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A programming challenge with no binary and no service: evaluate a degree-8 polynomial from nine coefficients and a value of `x`, then print the result. The only trap is getting the exponents right; Horner's scheme does it in one line without large powers.

## Statement and surface

- **Coding** category, **Very Easy** difficulty.
- No files: the platform shows the statement and an editor that accepts C, C++, Python or Rust.
- Input: the nine coefficients `a0 … a8` on one line and the integer `x` on the next.
- Output: `P(x) = a0 + a1·x + a2·x² + … + a8·x⁸`.

```text
Input
1 -2 3 -4 5 -6 7 -8 9
5

Output
2983941
```

## Recon

There is no surface to enumerate, only an input/output contract:

- Coefficients are ordered from lowest to highest degree (`a0` first).
- `x` may be negative, so even powers stay positive and odd powers flip sign.
- The result fits in a 64-bit integer for the challenge's ranges; Python does not care.

## Code analysis

There is no existing code. The problem asks for a polynomial evaluation, not a root or a derivative.

The direct form sums `coefficient * x**index`. Horner avoids computing powers and uses nine multiplications:

```text
P(x) = a0 + x·(a1 + x·(a2 + … + x·a8))
```

## Root cause

There is no vulnerability: the exercise measures implementation accuracy. Typical mistakes are off-by-one indexing (starting at `a1`), sign errors with a negative `x`, and reading both lines as a single input.

## Local reproduction

```bash
python3 evaluative.py <<'EOF'
1 -2 3 -4 5 -6 7 -8 9
5
EOF
```

```python
# evaluative.py
coeffs = list(map(int, input().split()))
x = int(input())

result = 0
for c in reversed(coeffs):
    result = result * x + c
print(result)
```

The `enumerate` variant returns the same value and reads more clearly:

```python
print(sum(c * x**i for i, c in enumerate(coeffs)))
```

## Exploitation

1. Read the coefficients with `input().split()`.
2. Read `x` with `int(input())`.
3. Evaluate with Horner and `print`.
4. Submit the output; the environment returns the flag when it matches.

## Evidence

- Local run of the sample producing `2983941`.
- No real flag in this writeup.

## Lessons learned

- Horner is not only an optimisation: it avoids intermediate overflow from large powers.
- Confirming coefficient order up front saves debugging a result that is "almost" right.
- Reading the whole input (two lines) is part of the problem, not a detail.
- In coding challenges the statement is usually the only specification; there are no visible tests beyond the sample.

## Mitigations and detection

- No security mitigation applies; this is a programming exercise.
- In production code the takeaway is to validate ranges and use wide enough integers.
- Detection: none, there is no exposed component.

## References

- <https://www.hackthebox.com/challenges/evaluative>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/evaluative/>
- <https://tiemenruijgrok.com/posts/2025/07/HTB_Evaluative_Writeup>
- <https://medium.com/@kezosec/evaluative-htb-coding-challenge-writeup-4cbf2661da5a>
