---
topic: ELF analysis
tags: [reversing, elf, ghidra, gdb, readelf, binary]
---

# ELF analysis

**English** | [🇪🇸 Español](elf-analysis.md)

## Concept

An ELF binary is analysed in three layers: headers and symbols, disassembled code and runtime behaviour. `readelf`, `objdump`, Ghidra and GDB move from static structure to logic and exploitation.

## When it applies

- Reversing or pwn challenges.
- A binary without source code.
- Searching for validation functions.
- Checking protections before an exploit.

## Procedure

1. Identify architecture, bits and linking.
2. Review symbols, imports and strings.
3. Disassemble or decompile in Ghidra.
4. Run under GDB and observe calls.
5. Document logic and protections.

```bash
file ./binary
checksec --file=./binary
readelf -h ./binary
readelf -s ./binary | head
objdump -d -M intel ./binary | head
gdb -q ./binary
```

## Variants

- Static or dynamic binary.
- Stripped symbols.
- PIE, NX, canary and RELRO.
- Branch comparisons and cryptographic functions.

## Limitations

- Decompilation may lose types.
- The binary may be packed.
- The architecture may need emulation.
- GDB needs permissions and a compatible environment.

## Mitigation and detection

- Do not treat obfuscation as protection.
- Sign and verify binaries.
- Apply compiler protections.
- Monitor execution of unsigned binaries.

## References

- <https://man7.org/linux/man-pages/man5/elf.5.html>
- <https://ghidra-sre.org/>
- <https://sourceware.org/gdb/documentation/>
