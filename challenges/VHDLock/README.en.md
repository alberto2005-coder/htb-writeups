---
challenge: VHDLock
type: Hardware
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [hardware, vhdl, fpga, xor, simulation, ghdl]
---

# VHDLock — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The challenge provides a VHDL design implementing a "lock". Reading the data flow reveals an XOR with a constant and a comparison; simulating the circuit or reversing the operation yields the flag.

## Prompt and surface

- Hardware, Medium, retired.
- `.vhd` files, a testbench and possibly a capture are provided.
- No remote service.

```bash
ls
file *.vhd
```

## Reconnaissance

Identify entities and ports: `clk`, `reset`, `data_in`, `data_out`, `valid`. The testbench drives stimuli and shows the output.

```bash
ghdl -a *.vhd
ghdl -e tb_lock
ghdl -r tb_lock --vcd=lock.vcd
gtkwave lock.vcd
```

## Analysis

1. Follow `data_in` to the output register.
2. Locate the XOR operation and constant.
3. Identify the comparison with the expected value.
4. Reverse the transform (`cipher XOR key`) to recover ASCII.
5. Validate the sequence with the testbench.

```python
ct = bytes.fromhex('<ciphertext>')
key = b'<key>'
print(bytes(c ^ key[i % len(key)] for i, c in enumerate(ct)))
```

## Root cause

The "protection" is a reversible transform without a strong secret. The design and key are in the entregable, so simulation reveals the flow.

## Local reproduction

1. Compile with GHDL.
2. Run the testbench and inspect waves.
3. Extract the XOR constant.
4. Decode the text.
5. Verify the result.

## Evidence

- VHDL files and testbench.
- Waveform capture.
- Decoder script and redacted flag.

## Lessons learned

- VHDL is readable code, not a black box.
- XOR with a fixed key is reversible.
- GHDL/GTKWave expose the flow.
- Simulation is faster than synthesis.

## Mitigation and detection

- Do not use XOR with an embedded key as protection.
- Use standard cryptography and key management.
- Protect the bitstream/design.
- Validate on hardware with authentication.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/vhdlock/>
- <https://ghdl.github.io/ghdl/>
- <https://gtkwave.sourceforge.net/>
