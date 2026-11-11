---
challenge: Sneak peek
category: Challenge
type: ics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, modbus, custom-protocol, pymodbus, md5, plc]
---

# Sneak peek — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A PLC with a proprietary protocol on top of Modbus/TCP (function `0x64`) exposing three commands: read memory (`0x20`), write memory (`0x21`) and get the secret (`0x22`). Only the last one asks for a password, and its MD5 hash lives in a memory block that is **writable without authentication**. The solution is to read the block, locate the hash, replace it with the MD5 of a known password and request the secret.

## Statement and surface

- **ICS** category, **Easy** difficulty; Business CTF 2024.
- Online instance plus an archive with `protocol_information.png` and `client.py` (`ModbusRequest`/`ModbusResponse` wrappers).
- The hint: the password is stored in the memory block as an "uncrackable" MD5 hash.

## Recon

The protocol document describes:

| Command | Code | Data | Response |
|---|---:|---|---|
| `read_memory_block` | `0x20` | `addr[3] + length` | bytes read |
| `write_memory_block` | `0x21` | `addr[3] + data` | `[1]` on success |
| `get_secret` | `0x22` | password in clear | secret (the flag) |

- 16 KiB memory block; `length` is a single byte, so at most 256 bytes per request.
- Error code `0xE009`: invalid password.
- Only `get_secret` checks a password; reads and writes are unauthenticated.

## Code analysis

`client.py` registers a response class for function `0x64` in the pymodbus framer; `encode`/`decode` is a `struct.pack` of session, code and data. That is enough to send all three commands.

The flaw is in the trust model: password verification compares the supplied MD5 with the one stored in memory, but that block is written with `0x21` without any check. Replacing the hash with one you know is equivalent to changing the password.

## Root cause

Authorization based on data the client can modify. There is no authentication on `write_memory_block` and no protection for the region holding the hash. It is an **integrity of authentication data** case: if the attacker can write it, the check is worthless.

## Local reproduction

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusSocketFramer
import hashlib

client = ModbusTcpClient(HOST, port=PORT, framer=ModbusSocketFramer)
client.framer.decoder.register(CustomProtocolResponse)   # class from client.py

# 1) read all 16 KiB in 255-byte chunks and concatenate
# 2) locate the 16-byte entry (hash) and its index
# 3) write the MD5 of "new_password" at index+offset, offset 0..5
# 4) get_secret with "new_password"
client.write...  # replaced by send_packet(client, SESSION, 0x21, addr + md5_bytes)
```

The entry index and the five bytes around it change per instance, so the solver tries all six offsets until `get_secret` stops returning `0xE009`.

## Exploitation

1. Read the whole memory block (64 reads of 255 bytes; stop on `0xFF`).
2. Split entries on the `0x00` byte and keep the 16-byte one: that is the MD5.
3. Compute the MD5 of a known password and overwrite the entry.
4. Call `0x22` with that password; the response is the flag's ASCII bytes.

## Evidence

- `write_memory_block` returns `[1]` and `get_secret` stops returning `0xE009`.
- The response contains an ASCII sequence in flag format.
- Flag truncated in this writeup.

## Lessons learned

- A proprietary protocol on Modbus is analysed from its documentation and codes, not by guessing.
- Unauthenticated read/write commands turn any access control into decoration.
- Size limits (one length byte) force iteration and careful address bookkeeping.
- Trying offsets around a found entry is faster than understanding every padding byte.

## Mitigations and detection

- Write-protect the credential region and authenticate any `write_memory_block`.
- Never derive authorization from a hash stored in process memory reachable over the network.
- Detection: writes to configuration addresses, non-standard function codes and sequential reads of the whole block.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) and T0855 (Unauthorized Command Message).

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/ics/Sneak%20peek%20%5BEasy%5D>
- <https://github.com/hackthebox/business-ctf-2024>
- <https://pymodbus.readthedocs.io/>
