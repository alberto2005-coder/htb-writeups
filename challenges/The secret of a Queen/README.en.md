---
challenge: The secret of a Queen
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, cipher, substitution, mary-queen-of-scots]
---

# The secret of a Queen — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides text encrypted with a monoalphabetic substitution linked to Mary, Queen of Scots. Identify frequent words and solve the alphabet by frequency and context until the flag is readable.

## Statement and surface

- Misc, Very Easy, retired.
- A ciphertext and a historical hint are provided.
- The alphabet may be mixed or shifted.

```bash
cat cipher.txt
wc -c cipher.txt
```

## Reconnaissance

- Count letter and word frequencies.
- Look for three-letter patterns (`the`, `and`).
- Check for numbers or symbols standing for letters.
- Identify the likely language.

## Cipher analysis

Substitution preserves word structure. Build a mapping: the most frequent letters are usually `e`, `a`, `o`; one-letter words are `a`/`I`; three-letter words are `the`/`and`. Context resolves ambiguities.

```python
from collections import Counter
text = open('cipher.txt').read().lower()
print(Counter(c for c in text if c.isalpha()).most_common())
```

## Flaw explanation

Classical encryption does not resist frequency analysis or known plaintext. The historical hint narrows the search and allows trying known alphabets.

## Local reproduction

```bash
python3 - <<'PY'
import string
cipher = open('cipher.txt').read()
print(cipher.translate(str.maketrans('ABC...', 'abc...')))
PY
```

## Exploitation

Try a substitution alphabet, correct words and validate with a dictionary. The flag appears at the end or in a marked phrase.

## Evidence

- Frequencies and candidate words.
- Substitution table.
- Readable plaintext.
- Flag redacted.

## Lessons learned

- Frequency is the first classical cryptanalysis tool.
- Historical context can supply the alphabet.
- Monoalphabetic substitution is not secure.

## Mitigations and detection

- Use modern authenticated encryption for real secrets.
- Do not rely on historical substitutions.
- Document the alphabet and key for exercises.
- References: Mary Queen of Scots, monoalphabetic substitution, HTB The secret of a Queen.

## References

- <https://www.hackthebox.com/challenges/The%20secret%20of%20a%20Queen>
- <https://7rocky.github.io/en/ctf/htb-challenges/misc/the-secret-of-a-queen/>
- <https://en.wikipedia.org/wiki/Substitution_cipher>
- <https://attack.mitre.org/techniques/T1140/>
