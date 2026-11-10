---
challenge: Impossible Password
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, gdb, strcmp, srand, radare2]
---

# Impossible Password — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Challenge solved; no real flags.
> Sources disagree between Very Easy and Easy; it is documented as Easy.

## TL;DR

An ELF asks for two passwords. The first is compared to a fixed string (`SuperSeKretKey`) with a plain `strcmp`. The second is **not**: the program seeds `srand(time(0))`, allocates memory and generates the expected string with `rand()` at runtime, so it does not exist inside the binary. Instead of guessing it, set a breakpoint on the second `strcmp` and make both arguments equal: the comparison returns 0 and the program prints the flag.

## Brief and surface

- Reversing, retired.
- A single file is shipped: `impossible_password.bin`.
- No URL or container: everything happens locally.

## Recon

```bash
file impossible_password.bin
checksec --file=impossible_password.bin
strings -a impossible_password.bin | head -30
```

```text
impossible_password.bin: ELF 64-bit LSB executable, x86-64, dynamically linked
```

`strings` shows the welcome message and the first password, but not the second: it is never stored.

```bash
chmod +x impossible_password.bin
./impossible_password.bin
# *  (asks for the first)
# SuperSeKretKey
# ** (asks for the second)
```

## Source analysis

`main` has two comparison blocks:

```c
printf("* ");
__isoc99_scanf("%20s", buf1);
if (strcmp(buf1, "SuperSeKretKey") != 0) exit(1);

srand(time(0));
char *expected = malloc(0x11);
for (i = 0; i < 0x10; i++)
    expected[i] = rand() % 94 + 33;      /* printable ASCII */
expected[0x10] = 0;

printf("** ");
__isoc99_scanf("%20s", buf2);
if (strcmp(buf2, expected) != 0) exit(1);

give_flag();
```

The second string depends on the clock: two runs in different seconds expect different values. That is why "the password" does not exist, and why the challenge is named that way.

## The bug

There is no memory corruption or misused `strcmp`: the flaw is in the **design of the check**. The program compares user input against a value it computes itself, inside the same address space. Any attacker with a debugger can point both pointers at the same string without predicting `rand()`.

It is the local equivalent of a server validating a token by comparing it to the one it generated in memory: the check is correct, but the adversary controls the context.

## Local reproduction

```bash
gdb -q ./impossible_password.bin
```

```gdb
set disassembly-flavor intel
disassemble main
b *main+0x...        # address of the second strcmp (right after the second scanf)
run
SuperSeKretKey
AAAA
```

At the breakpoint:

```gdb
x/s $rdi
x/s $rsi
set $rdi = $rsi
continue
```

`x/s $rsi` prints the string generated for that run: it changes every second, confirming `srand(time(0))`.

## Exploitation

GDB path (shortest):

```bash
gdb -q ./impossible_password.bin -ex 'b strcmp' -ex 'run'
```

With the breakpoint on `strcmp`, the first call compares against `SuperSeKretKey`; continue (`c`), send anything as the second password, and at the second stop equalise the registers:

```gdb
set $rdi = $rsi
continue
```

The program takes the success branch and prints the flag.

radare2 path (no interactive debugger):

```bash
r2 -A impossible_password.bin
pdf @ main
px @ <string address>
```

The flag is built from bytes the binary transforms (XOR) before printing; once the routine is located, replicate it in a three-line script instead of running the binary.

## Evidence

- `x/s $rsi` with the random string and trimmed final output.
- No real flags: values live in `private/`.

## Lessons learned

- A `strcmp` against a runtime-generated value is intercepted, not guessed.
- `srand(time(0))` makes the check non-deterministic but also proves the value exists in memory before comparison.
- Equalising `$rdi`/`$rsi` on x86-64 is the universal shortcut past a string comparison.
- `strings` cannot find what is computed: read the flow, not just the binary.

## Mitigations and detection

- In real software a licence must not be validated against a value computed in the same process: use asymmetric signatures verified with a public key, and obfuscating the check does not fix the design.
- Detection (defence): not applicable to a CTF binary; in a product, debugger and memory-patch telemetry is noise and should not be a control.
- For analysis: record addresses and offsets for the exact build; without the version, the exploit is not reproducible.

MITRE: no applicable offensive ATT&CK technique; T1622 (debugger evasion) describes a defensive technique not used here.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/reversing/impossible-password>
- <https://dillonwu-97.github.io/csec-writeups/hackthebox/challenges/reversing/impossible-password>
- <https://sourceware.org/gdb/current/onlinedocs/gdb/>
- <https://cplusplus.com/reference/cstdlib/srand/>
