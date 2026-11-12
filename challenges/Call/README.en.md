---
challenge: Call
type: Crypto
difficulty: Unknown
platform: Hack The Box
state: Retired
tags: [crypto, audio, dtmf, primes, scripting]
---

# Call — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Official difficulty unconfirmed; reference writeup, not played.
> No flag or real DTMF sequence.

## TL;DR

The challenge provides `sound.mp3`. Convert it to WAV and demodulate with `multimon-ng` to reveal **DTMF** tones: a digit sequence. Read that sequence as prime-number indices and map them to letters (2 = A, 3 = B, 5 = C…). The result is the flag.

## 1. Inspect the audio

```bash
file sound.mp3
ffprobe -hide_banner sound.mp3
soxi sound.mp3
```

Check duration, channels and sample rate. DTMF tones sound like phone beeps; for long audio, locate them with a spectrogram:

```bash
ffmpeg -i sound.mp3 -lavfi showspectrumpic=s=1024x512 spec.png
```

## 2. Convert and demodulate

`multimon-ng` works best with mono PCM WAV:

```bash
ffmpeg -i sound.mp3 -ar 8000 -ac 1 -c:a pcm_s16le sound.wav
multimon-ng -t wav -a DTMF sound.wav
```

The output is a list of digits, e.g. repeated `DTMF: 5`. Clean and concatenate:

```bash
multimon-ng -t wav -a DTMF sound.wav | grep -oE 'DTMF: [0-9]' | awk '{print $2}' | tr -d '\n'
```

If nothing is detected, try another filter or normalise gain:

```bash
sox sound.wav norm.wav norm
multimon-ng -t wav -a DTMF norm.wav
```

## 3. The prime cipher

Each letter is represented by a prime:

```text
A=2  B=3  C=5  D=7  E=11  F=13  G=17  H=19  I=23  J=29
K=31 L=37 M=41 N=43 O=47  P=53  Q=59  R=61  S=67  T=71
U=73 V=79 W=83 X=89 Y=97  Z=101
```

The DTMF sequence gives those primes, usually separated by `0` or `1` (not prime, used as separators). Decode with a script:

```python
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101]
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
seq = '<DTMF_DIGITS>'.replace('0', ' ').replace('1', ' ')
out = ''.join(alphabet[primes.index(int(n))] for n in seq.split())
print(out)
```

If the sequence has no separators, try grouping in pairs or use the primes as positions.

## 4. Variants

- **Primes as positions**: the number is the alphabet index, not the prime value.
- **A1Z26**: group DTMF digits in pairs and map directly (`01`=A, `02`=B…).
- **Two layers**: DTMF → phone number → coordinates → text. Try the simplest hypothesis first.
- **Reversed audio**: if tones do not decode, `sox sound.wav reverse.wav reverse`.

## 5. Verify

The text should be readable and match `HTB{...}`. If it is gibberish, check:

- Digit order.
- Separators (`0`/`1`).
- A tone lost while trimming.
- Whether the mapping is inverted (A=101, Z=2).

## Lessons learned

- DTMF is a telephone standard; `multimon-ng` decodes it without a custom decoder.
- A “prime cipher” may be direct substitution or an index; test both.
- A spectrogram reveals hidden tones or noise.
- Converting to mono WAV avoids decoding failures.
- Validate the flag by format, not intuition.

## Mitigations (for challenges)

- Keep the original audio and work on copies.
- Record sample rate and filter used.
- Do not assume the first result is right: test the inverse.

MITRE: T1027, T1140.

## References

- <https://inesmartins.github.io/htb-crypto-challenge-call/index.html>
- <https://github.com/EliasOenal/multimon-ng>
- <https://en.wikipedia.org/wiki/Dual-tone_multi-frequency_signaling>
