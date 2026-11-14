---
challenge: Walkie Hackie
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, rf, iq, signal, demodulation]
---

# Walkie Hackie — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides an IQ capture of a radio conversation. Identify the center frequency and bandwidth, demodulate the signal and decode tones or voice to recover the flag.

## Statement and surface

- Hardware, Easy, retired.
- An IQ file (`complex16s` or similar) is provided.
- The prompt mentions a walkie-talkie.

```bash
file capture.iq
python3 -c 'import numpy as np; print(np.fromfile("capture.iq", dtype=np.complex64)[:5])'
```

## Reconnaissance

- Open the capture in `inspectrum` or `Universal Radio Hacker`.
- Identify the carrier and bandwidth.
- Check the spectrogram for bursts and shifts.
- Determine the modulation (FM, AM, FSK).

## Signal analysis

The signal is narrowband FM. Shift the center frequency to baseband, apply an FM demodulator and filter the audio. If voice is unintelligible, try decimation factors and check for DTMF tones.

```python
import numpy as np
from scipy.signal import butter, filtfilt

iq = np.fromfile('capture.iq', dtype=np.complex64)
audio = np.angle(iq[1:] * np.conj(iq[:-1]))
```

## Flaw explanation

The communication is not encrypted. The capture holds enough information to demodulate and hear or decode the message; the only difficulty is identifying signal parameters.

## Local reproduction

```bash
inspectrum -r 1e6 capture.iq
# Adjust frequency, bandwidth and demodulation
```

## Exploitation

Save the demodulated audio, play it and transcribe the message. The flag may be in voice, DTMF tones or modulated text.

## Evidence

- Spectrogram with the carrier.
- Intelligible demodulated audio.
- Decoded tones or text.
- Flag redacted.

## Lessons learned

- An IQ capture preserves the whole signal.
- FM demodulation is a phase difference.
- DTMF tones are decoded with Goertzel.

## Mitigations and detection

- Use encrypted, authenticated radios.
- Never transmit secrets over analog channels.
- Monitor unauthorized emissions.
- References: GNU Radio, Inspectrum, HTB Walkie Hackie.

## References

- <https://www.hackthebox.com/challenges/Walkie%20Hackie>
- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/walkie-hackie/>
- <https://github.com/gnuradio/gnuradio>
- <https://attack.mitre.org/techniques/T1040/>
