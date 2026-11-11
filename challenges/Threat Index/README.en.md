---
challenge: Threat Index
category: Challenge
type: coding
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [coding, python, string-matching, weighted-score, stdin-stdout]
---

# Threat Index — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

Score a simulated traffic string by summing, for each keyword, its occurrences times a fixed weight (1 to 18). No binary or service: walk an 18-entry dictionary and count occurrences. The only design question is overlapping versus non-overlapping counts, and with these keywords it makes no difference.

## Statement and surface

- **Coding** category, **Very Easy** difficulty.
- Editor on the platform (C, C++, Python or Rust), no attachments.
- Input: a lowercase alphanumeric string between 30 and 10⁶ characters.
- Output: `Σ (occurrences × weight)`.

| Weight | Keyword | Weight | Keyword |
|---:|---|---:|---|
| 1 | `scan` | 10 | `inject` |
| 2 | `response` | 11 | `execute` |
| 3 | `control` | 12 | `deploy` |
| 4 | `callback` | 13 | `malware` |
| 5 | `implant` | 14 | `exploit` |
| 6 | `zombie` | 15 | `payload` |
| 7 | `trigger` | 16 | `backdoor` |
| 8 | `infected` | 17 | `zeroday` |
| 9 | `compromise` | 18 | `botnet` |

```text
Input
payloadrandompayloadhtbzerodayrandombytesmalware

Output
60
```

(`payload` twice × 15 = 30, `zeroday` 17, `malware` 13.)

## Recon

- The string only contains lowercase letters and digits, so there is no case folding to do.
- The terms do not overlap in practice, so Python's `count` is enough.
- Length reaches 10⁶: scan once per keyword (18 passes) instead of building substrings.

## Code analysis

```python
weights = {
    "scan": 1, "response": 2, "control": 3, "callback": 4,
    "implant": 5, "zombie": 6, "trigger": 7, "infected": 8,
    "compromise": 9, "inject": 10, "execute": 11, "deploy": 12,
    "malware": 13, "exploit": 14, "payload": 15, "backdoor": 16,
    "zeroday": 17, "botnet": 18,
}

stream = input().strip()
print(sum(stream.count(k) * w for k, w in weights.items()))
```

Complexity is `O(18 · n)`, fine for 10⁶. An Aho-Corasick automaton would be faster but is unnecessary.

## Root cause

No vulnerability; the exercise tests a weighted sum without mixing up the weights. Typical mistakes are confusing weight with position, omitting a keyword, or counting on a string that was already consumed.

## Local reproduction

```bash
printf '%s\n' 'payloadrandompayloadhtbzerodayrandombytesmalware' | python3 threat_index.py
# 60
```

## Exploitation

1. Read the whole string with `input().strip()`.
2. Walk the dictionary and add `count × weight`.
3. Submit; the platform validates the result.

## Evidence

- Local output `60` for the statement's sample.
- No real flag in this writeup.

## Lessons learned

- Reading the statement together with the weight table prevents inventing weights.
- `str.count` counts non-overlapping substrings; overlapping terms would need another approach.
- With million-character inputs, measure before optimising: 18 passes are cheap.

## Mitigations and detection

- No security mitigation applies.
- In a real system the equivalent is a rule engine with versioned weights and input size limits.

## References

- <https://www.hackthebox.com/challenges/threat-index>
- <https://chrispham-cyber.github.io/posts/Threat-Index/>
- <https://motasem-notes.net/practical-coding-in-cyber-security-hackthebox-coding-challenges>
- <https://7rocky.github.io/en/ctf/htb-challenges/coding/>
