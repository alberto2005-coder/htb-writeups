---
topic: PyInstaller binary extraction
tags: [forensics, pyinstaller, python, bytecode, reversing, malware]
---

# PyInstaller binary extraction

**English** | [🇪🇸 Español](pyinstaller-extraction.md)

## Concept

PyInstaller bundles a Python program, its dependencies and the interpreter into one executable. The file contains an archive with `.pyc` bytecode; it can be extracted and decompiled to recover logic, keys and strings.

## When it applies

- Executables with Python strings or `pyinstaller` references.
- Python-based malware.
- Internal tools distributed as binaries.
- Reversing and forensics challenges.

## Procedure

1. Identify the binary with `file` and `strings`.
2. Confirm PyInstaller via `MEI` or `pyi-` strings.
3. Extract with `pyinstxtractor`.
4. Locate the main `.pyc` and fix its header if missing.
5. Decompile with `uncompyle6` or `decompyle3`.

```bash
python3 pyinstxtractor.py sample.exe
python3 -m uncompyle6 sample.exe_extracted/sample.pyc
```

## Variants

- Bytecode without the magic header, requiring restoration.
- Python versions without a direct decompiler.
- Key encrypted by a native loader.
- Single-stage binaries with embedded resources.

## Limitations

- The Python version must match the decompiler.
- Bytecode may be obfuscated or modified.
- Recent binaries may include a loader that encrypts the key.
- Extraction does not guarantee exact source recovery.

## Mitigation and detection

- Do not rely on executable opacity as protection.
- Sign binaries and verify their origin.
- Analyze in a sandbox before running.
- Alert on processes extracting temp files and launching Python.

## References

- <https://github.com/extremecoders-re/pyinstxtractor>
- <https://pyinstaller.org/en/stable/operating-mode.html>
- <https://attack.mitre.org/techniques/T1027/009/>
- <https://attack.mitre.org/techniques/T1059/006/>
