---
challenge: Aptitude Test
category: Misc
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, nc, socket, quiz]
---

# Aptitude Test — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A quiz over a socket: ten scenario questions with four options (`A`–`D`). Correct answers are not checked; any answer moves on. Sending `A` ten times reaches the end, where the service assigns a role and returns the flag. The "challenge" is using `nc` and not dropping the connection.

## Brief and surface

- Misc, Very Easy; Business CTF 2024.
- Only a host and port are given: no binary, no source.
- The story is an aptitude test that assigns a role within the team.

## Recon

```bash
nc <IP> <PORT>
```

The service prints an intro and the first question with four options. Each answer brings the next one; at the end it shows the assigned role and the flag.

## Source analysis

There is no code to read. Behaviour comes from the interaction:

- Upper and lower case both work (`a` and `A`).
- No visible timer or attempt limit inside the session.
- The connection is linear: closing it starts over.
- Ten questions, so scripting is not worth it.

## The bug

This is not a vulnerability: it is a socket-handling exercise. The only "weakness" is that the outcome does not depend on being right, only on finishing the quiz. The service is meant to practise `nc` and prompt reading.

## Local reproduction

Not applicable: the challenge is a remote instance and the server is not shipped. It can be simulated with a script that prints questions and reads answers, but that adds nothing to the method.

## Exploitation

1. Connect with `nc <IP> <PORT>`.
2. Read the question and type `A` (or `a`) followed by Enter.
3. Repeat ten times.
4. Note the role and the flag the service prints.

Optional automation with `pwntools`, useful to avoid copy-paste:

```python
from pwn import remote

io = remote("<IP>", <PORT>)
for _ in range(10):
    io.recvuntil(b"> ")
    io.sendline(b"A")
print(io.recvall().decode(errors="replace"))
```

The exact question count comes from the output; the official one is ten.

## Evidence

- A transcript of the ten questions and answers.
- The assigned role and the flag at the end; kept in `private/`.

## Lessons learned

- **Correctness is irrelevant**: the quiz does not score, it only advances.
- **Linear connection**: closing `nc` forces a restart; keep the terminal stable.
- **Scripting is unnecessary**: with ten questions, automating costs more than answering.

## Mitigations and detection

- If a real quiz must assess someone, scoring belongs on the server and must not accept any option as valid.
- A test service should not hand out secrets for merely completing the flow without validating answers.
- Detection: sessions that answer the same option on every item; rate limits and per-question validation.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BVery%20Easy%5D%20Aptitude%20Test>
- <https://www.kali.org/tools/netcat/>
- <https://docs.pwntools.com/en/stable/remote.html>
