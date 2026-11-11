---
challenge: Tear or Dear
category: Reversing
type: Reversing
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [reversing, dotnet, dnspy, windows, winforms]
---

# Tear or Dear — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags or credentials.

## TL;DR

A .NET WinForms login (`TearOrDear.exe`) asks for a username and password. The code is full of chained methods and meaningless names, but the final check is a single line: `this.username == this.o && this.check1(s)`. With **32-bit dnSpy**, break there and read both expected values from locals; the credentials are the flag body. Understanding all the obfuscation is unnecessary.

## Brief and surface

- Reversing, Medium.
- Ships `TearOrDear.exe`, a PE32 GUI built from C# .NET.
- The story is a login to bypass; the flag is the credential that opens it.

## Recon

```bash
file TearOrDear.exe
```

```text
PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
```

Running it on Windows shows a form with `User Name` and `Password` boxes and a `Login` button. Any wrong pair leaves `WRONG CREDENTIALS! Try Again...` in red.

## Source analysis

dnSpy (or ILSpy/dotPeek) returns near-original C#. The relevant parts:

- `button1_Click` calls `kapa()`, which fills `this.o` character by character through `linear` and `expo`.
- It then computes `this.aa = Multiply(encrypted1(textBox_user.Text).Substring(0, 5), -1)` and drops the last character.
- `Multiply` **reverses** the string and, on the way, assigns `this.username = textBox_pass.Text`.
- `check1` chains `check2`, `check3`, `check4` and `check`, which finally compares `textBox_user.Text` with `this.aa`.
- The deciding condition is `this.username == this.o && this.check1(s)`.

There are deliberate distractions: `oura = "p00f123#"`, `pepper = 10`, and an `encrypted1` recursion cut off after ten calls. None of them changes the final comparison.

## The bug

Authentication is **local and symmetric**: the program builds both expected values in memory (`this.o` for the password, `this.aa` for the username) and compares them with the input. No server, no hash, no external secret. Any client-side value can be read with a debugger.

## Local reproduction

The binary needs Windows or a VM with .NET Framework. It runs without installation and opens no ports or network connections.

## Exploitation

1. Open `TearOrDear.exe` in **32-bit dnSpy** (the process is 32-bit; the 64-bit build will not attach).
2. Break on `if (this.username == this.o && this.check1(s))` inside `button1_Click`.
3. Type any username and password, then click `Login`.
4. When the breakpoint hits, inspect `this.o` and `this.aa`: they are the expected password and username.
5. Rebuild `username:password` and wrap it in the challenge flag format.

The actual values are kept in `private/` and not published here.

## Evidence

- `TearOrDear.exe`, a PE32 .NET WinForms binary.
- A breakpoint in `button1_Click` with `this.o` and `this.aa` already computed.
- Credentials and flag in `private/`.

## Lessons learned

- **dnSpy architecture**: a 32-bit binary needs 32-bit dnSpy; otherwise it will not attach.
- **Do not chase the obfuscation**: `encrypted1` and `encrypted10` are noise; the final comparison is one line.
- **`this.username` changes**: `Multiply` overwrites it with the password, so the user and password checks cross over. Reading locals at the breakpoint avoids the confusion.

## Mitigations and detection

- Never validate credentials client-side: any local comparison is observable with a debugger.
- If the binary needs a secret, make it a public key and verify on the server.
- Detection (if seen in malware): .NET assemblies with random names, reversed strings and embedded credential comparisons; dnSpy and ILSpy are the usual triage.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/tear-or-dear/>
- <https://github.com/dnSpy/dnSpy>
- <https://github.com/icsharpcode/ILSpy>
