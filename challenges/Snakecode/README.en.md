---
challenge: Snakecode
category: Reversing
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, python, pyc, marshal, uncompyle6]
---

# Snakecode — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The challenge ships `chall.pyc`, **Python 2.7** bytecode. `uncompyle6` recovers a script that loads functions from base64 + zlib + `marshal` blobs and starts a `curses` Snake game. The "apple" (`$`) keeps changing character and writes the flag onto the board. Winning is unnecessary: instrument `snake()` to log its parameters, or cheat by raising the score and pinning the position, then read the characters.

## Brief and surface

- Reversing, Easy.
- A single file, `chall.pyc`.
- No source is provided, only compiled bytecode.

## Recon

```bash
file chall.pyc
```

```text
chall.pyc: python 2.7 byte-compiled
```

Running it opens a Snake game in the terminal. The binary takes no arguments and uses no network.

## Source analysis

Decompile inside a Python 2.7 container, because `uncompyle6` needs that version for 2.7 bytecode:

```bash
docker run -v "$PWD":/ctf -it python:2.7 bash
pip install uncompyle6
uncompyle6 chall.pyc > chall.py
```

The result imports `marshal`, `types` and `time`, and builds functions with:

```python
ll = types.FunctionType(marshal.loads(base64.b64decode(blob)), globals())
```

The blobs are zlib-compressed; `marshal` rebuilds the code object and `FunctionType` turns it into a function. The visible `snake()` only initialises state and loops over `m2`:

```python
def snake(w):
    r = i0(); c = i1(); f0(w)
    d = (0, 1); p = [(5, 5)]; pl = 1; s = 0; l = None
    while 1:
        p, d, pl, l, s, w, c, r = m2(p, d, pl, l, s, w, c, r)
        time.sleep(0.4)
```

- `p` holds the snake body coordinates.
- `pl` is the score and grows when eating.
- `d` is the direction; `s` the move counter.
- The apple changes character as the game advances and spells the flag.

## The bug

The flag is never compared: **it is displayed**. The game reveals it slowly, tied to state (eating apples), but that state lives in memory and can be changed. This is a secret in the execution flow, not cryptography.

## Local reproduction

With the Python 2.7 container and `curses` available, `python chall.py` opens the board. The game ends when the snake tangles, so instrument it before playing seriously.

## Exploitation

**Option A — log state.** Add logging inside `snake()`:

```python
with open('log.txt', 'a') as fd:
    ...
    fd.write('p=%s; d=%s; pl=%s; l=%s; s=%s\n' % (p, d, pl, l, s))
```

After a few moves, `log.txt` shows the apple position and the score; the flag characters show up in the apple.

**Option B — cheat.** Patch the loop so the snake cannot die and the apple refreshes every step:

```python
while 1:
    p, d, pl, l, s, w, c, r = m2(p, d, pl, l, s, w, c, r)
    pl += 1
    p = [(5, 5)]
    time.sleep(0.4)
```

The snake survives, the score climbs and every move paints the next character. Noting what appears on screen rebuilds the flag, which is kept in `private/`.

## Evidence

- `chall.pyc`, Python 2.7 bytecode.
- Functions rebuilt from base64 with `marshal` + zlib.
- The flag shows in the apple during play; not published.

## Lessons learned

- **Python version**: `uncompyle6` fails on 2.7 bytecode under Python 3; the `python:2.7` container saves half an hour of errors.
- **`marshal` is not encryption**: it only serialises code; anyone with the `.pyc` can rebuild it.
- **Playing is not the path**: the game is limited by snake length; instrumenting or cheating is faster.

## Mitigations and detection

- A shipped `.pyc` protects nothing: `uncompyle6`, `decompyle3` or `pycdc` recover the code.
- If bytecode must ship, keep secrets and validation logic out of it; verify on the server.
- Detection: `.pyc` files with high-entropy base64 blobs and `marshal.loads` calls are an obfuscation signal.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/snakecode/>
- <https://github.com/rocky/python-uncompyle6>
- <https://docs.python.org/3/library/marshal.html>
