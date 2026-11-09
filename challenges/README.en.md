# Challenges — Hack The Box

**English** | [🇪🇸 Español](README.md)

Index of solved challenges plus a category map to pick the next one. Each challenge has its own folder with `README.md` and `README.en.md`; unsolved ones get added once finished.

## Solved

| Challenge | Type | Difficulty | Technique | State | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM in `session.upload_progress`, use-after-free, ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [ES](Dark%20Embargo/README.md) | [Ver](Dark%20Embargo/README.en.md) |
| Emdee five for life | Web | Easy | MD5 against the clock: session handling, regex, hashing in a script | **Retired** | [ES](Emdee%20five%20for%20life/README.md) | [Ver](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | LDAP injection: `*` as user and password, wildcards in search | **Retired** | [ES](Phonebook/README.md) | [Ver](Phonebook/README.en.md) |
| Under Construction | Web | Easy | JWT algorithm confusion: HS256 signed with the public key | **Retired** | [ES](Under%20Construction/README.md) | [Ver](Under%20Construction/README.en.md) |

## Categories

HTB groups challenges into twelve categories. Counts are approximate and meant for planning, not as an exact inventory.

| Category | Approx. | What it trains | Note |
|---|---|---|---|
| Web | 75+ | XSS, SQLi, SSTI, SSRF, deserialization, JWT | Best starting point |
| Crypto | 93+ | RSA, AES, ECC, padding oracle, custom ciphers | Heavy maths, light tooling |
| Pwn | 61+ | stack/heap, ROP, format string, UAF | Needs binaries and a debugger |
| Reversing | 44+ | x86/x64, ARM, .NET, Java, obfuscation | Pair with Ghidra/IDA |
| Misc | 35+ | scripting, logic, PyJail, encoding | Very varied |
| Forensics | 33+ | memory, disk, network, logs | Pairs with Sherlocks |
| OSINT | 12+ | geolocation, social media, metadata | No lab required |
| Stego | 12+ | LSB, steghide, audio, images | Quick practice |
| Hardware | 11+ | UART, SPI, I2C, firmware | Needs hardware or emulation |
| Mobile | 10+ | APK, Frida, smali, root detection | Android Studio |
| Blockchain | 10+ | Solidity, contracts, DeFi | Foundry/Remix |
| AI/ML | 5+ | adversarial ML, prompt injection | The newest one |

## Conventions

- One directory per challenge, named exactly as it appears on HTB.
- Spanish `README.md` and English `README.en.md`, with front matter (`challenge`, `type`, `difficulty`, `state`, `tags`).
- No flags: evidence is trimmed and redacted.
- If the challenge ships code or a binary, keep it next to the writeup only when it is redistributable.

## Template

`templates/challenge-template.md` and `templates/challenge-template.en.md`.

## Sherlocks

Defensive investigation scenarios are not attack challenges and live elsewhere: [sherlocks/README.en.md](../sherlocks/README.en.md) · [ES](../sherlocks/README.md).
