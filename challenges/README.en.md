# Challenges — Hack The Box

**English** | [🇪🇸 Español](README.md)

Index of solved challenges plus a category map to pick the next one. Each challenge has its own folder with `README.md` and `README.en.md`; unsolved ones get added once finished.

## Solved

| Challenge | Type | Difficulty | Technique | State | ES | EN |
|---|---|---|---|---|---|---|
| ropme | Pwn | Easy | Ret2libc with a `puts@got` leak: libc base and `system("/bin/sh")` | **Retired** | [ES](ropme/README.md) | [Ver](ropme/README.en.md) |
| Easy Phish | OSINT | Very Easy | `?all` SPF and `p=none` DMARC on the legitimate domain | **Retired** | [ES](Easy%20Phish/README.md) | [Ver](Easy%20Phish/README.en.md) |
| Hidden in Colors | Stego | Easy | PNG LSB with `zsteg` and per-channel reading | **Retired** | [ES](Hidden%20in%20Colors/README.md) | [Ver](Hidden%20in%20Colors/README.en.md) |
| Bare Metal | Hardware | Easy | 3.3 V UART, U-Boot and rootfs extraction with `binwalk` | **Retired** | [ES](Bare%20Metal/README.md) | [Ver](Bare%20Metal/README.en.md) |
| Cryptohorrific | Mobile | Easy | iOS app: base64 blob in the plist, AES key inside the Mach-O binary | **Retired** | [ES](Cryptohorrific/README.md) | [Ver](Cryptohorrific/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM in `session.upload_progress`, use-after-free, ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [ES](Dark%20Embargo/README.md) | [Ver](Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | MD5 against the clock: session handling, regex, hashing in a script | **Retired** | [ES](Emdee%20five%20for%20life/README.md) | [Ver](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | LDAP injection: `*` as user and password, wildcards in search | **Retired** | [ES](Phonebook/README.md) | [Ver](Phonebook/README.en.md) |
| Under Construction | Web | Easy | JWT algorithm confusion: HS256 signed with the public key | **Retired** | [ES](Under%20Construction/README.md) | [Ver](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | PHP object injection: `PageModel::__destruct` includes a file (LFI) and nginx log poisoning | Retired | [ES](Toxic/README.md) | [Ver](Toxic/README.en.md) |
| LoveTok | Web | Easy | `eval` sobre el formato de fecha; `addslashes` no frena `${}` | Retired | [ES](LoveTok/README.md) | [Ver](LoveTok/README.en.md) |
| Templated | Web | Easy | SSTI de Jinja2 en `render_template_string` | Retired | [ES](Templated/README.md) | [Ver](Templated/README.en.md) |
| baby ninja jinja | Web | Easy | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | Retired | [ES](baby%20ninja%20jinja/README.md) | [Ver](baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Easy | SSTI de Mako: `self.module` hasta `os` | Retired | [ES](Spookifier/README.md) | [Ver](Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Bundle JS con endpoints ocultos; comando secreto por API | Retired | [ES](Flag%20Command/README.md) | [Ver](Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | SSTI de Velocity: `#set` y reflexión de Java | Retired | [ES](Labyrinth%20Linguist/README.md) | [Ver](Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Contaminación de prototipos en Node hasta `child_process` | Retired | [ES](breaking%20grad/README.md) | [Ver](breaking%20grad/README.en.md) |
| Weather App | Web | Easy | SSRF with *response splitting* and SQLi in the internal service up to admin account takeover | **Retired** | [ES](Weather%20App/README.md) | [Ver](Weather%20App/README.en.md) |
| Freelancer | Web | Easy | SQLi en el login y `UNION SELECT` para extraer la flag | Retired | [ES](Freelancer/README.md) | [Ver](Freelancer/README.en.md) |
| Passman | Web | Easy | GraphQL IDOR in `UpdatePassword`: changing the admin password | **Retired** | [ES](Passman/README.md) | [Ver](Passman/README.en.md) |
| Cartographer | Web | Easy | SQLi in the login form and `panel.php?info=flag` | **Retired** | [ES](Cartographer/README.md) | [Ver](Cartographer/README.en.md) |
| Dynastic | Crypto | Very Easy | Trithemius cipher: the shift is the index | **Retired** | [ES](Dynastic/README.md) | [Ver](Dynastic/README.en.md) |
| Makeshift | Crypto | Very Easy | Reversal plus permutation of three-byte blocks | **Retired** | [ES](Makeshift/README.md) | [Ver](Makeshift/README.en.md) |
| Primary Knowledge | Crypto | Very Easy | RSA with a prime `n` → φ = n − 1 | **Retired** | [ES](Primary%20Knowledge/README.md) | [Ver](Primary%20Knowledge/README.en.md) |
| Iced Tea | Crypto | Easy | 32-round TEA with `delta` and a 32-bit mask | **Retired** | [ES](Iced%20Tea/README.md) | [Ver](Iced%20Tea/README.en.md) |
| Illumination | Forensics | Easy | Leaked `.git`: the token survives in history, base64-encoded | **Retired** | [ES](Illumination/README.md) | [Ver](Illumination/README.en.md) |
| MarketDump | Forensics | Easy | Export HTTP objects and decode the outlier as base58 | **Retired** | [ES](MarketDump/README.md) | [Ver](MarketDump/README.en.md) |
| Took the Byte | Forensics | Easy | Single-byte XOR (`0xFF`) down to a ZIP holding the password file | **Retired** | [ES](Took%20the%20Byte/README.md) | [Ver](Took%20the%20Byte/README.en.md) |
| Deadly Arthropod | Forensics | Medium | Rebuild keystrokes from USB keyboard HID reports | **Retired** | [ES](Deadly%20Arthropod/README.md) | [Ver](Deadly%20Arthropod/README.en.md) |
| Obscure | Forensics | Easy | Obfuscated webshell, PCAP with commands and a `.kdbx` cracked with john | **Retired** | [ES](Obscure/README.md) | [Ver](Obscure/README.en.md) |
| Keep Tryin' | Forensics | Medium | DNS exfiltration in base64url and RC4 with a weak key | **Retired** | [ES](Keep%20Tryin'/README.md) | [Ver](Keep%20Tryin'/README.en.md) |
| Alien Cradle | Forensics | Very Easy | Deobfuscate a PowerShell download cradle built from string concatenation | **Retired** | [ES](Alien%20Cradle/README.md) | [Ver](Alien%20Cradle/README.en.md) |
| Extraterrestrial Persistence | Forensics | Very Easy | base64-encoded systemd unit as the persistence mechanism | **Retired** | [ES](Extraterrestrial%20Persistence/README.md) | [Ver](Extraterrestrial%20Persistence/README.en.md) |
| Plaintext Tleasure | Forensics | Very Easy | Cleartext HTTP: credentials and flag inside the stream | **Retired** | [ES](Plaintext%20Tleasure/README.md) | [Ver](Plaintext%20Tleasure/README.en.md) |
| Urgent | Forensics | Very Easy | Phishing email: base64, URL encoding and a VBScript attachment | **Retired** | [ES](Urgent/README.md) | [Ver](Urgent/README.en.md) |
| BabyEncryption | Crypto | Very Easy | Affine map modulo 256 and the modular inverse | **Retired** | [ES](BabyEncryption/README.md) | [Ver](BabyEncryption/README.en.md) |
| Ancient Encodings | Crypto | Very Easy | Base64 inside hexadecimal, no key | **Retired** | [ES](Ancient%20Encodings/README.md) | [Ver](Ancient%20Encodings/README.en.md) |
| SpookyPass | Reversing | Very Easy | Cleartext password in the ELF's strings | **Retired** | [ES](SpookyPass/README.md) | [Ver](SpookyPass/README.en.md) |
| KORP Terminal | Web | Very Easy | Error-based SQLi and a cracked bcrypt hash | **Retired** | [ES](KORP%20Terminal/README.md) | [Ver](KORP%20Terminal/README.en.md) |
| TimeKORP | Web | Very Easy | Command injection through the time format | **Retired** | [ES](TimeKORP/README.md) | [Ver](TimeKORP/README.en.md) |
| Behind the Scenes | Reversing | Very Easy | `UD2` anti-decompilation and four `strncmp` calls in GDB | **Retired** | [ES](Behind%20the%20Scenes/README.md) | [Ver](Behind%20the%20Scenes/README.en.md) |
| OnlyHacks | Web | Very Easy | Stored XSS against a bot to steal its session cookie | **Retired** | [ES](OnlyHacks/README.md) | [Ver](OnlyHacks/README.en.md) |
| Perfect Synchronization | Crypto | Easy | AES-ECB and block-level frequency analysis | **Retired** | [ES](Perfect%20Synchronization/README.md) | [Ver](Perfect%20Synchronization/README.en.md) |
| xorxorxor | Crypto | Easy | Repeating-key XOR with a known prefix | **Retired** | [ES](xorxorxor/README.md) | [Ver](xorxorxor/README.en.md) |
| Baby Time Capsule | Crypto | Very Easy | RSA with small moduli: factor and decrypt | **Retired** | [ES](Baby%20Time%20Capsule/README.md) | [Ver](Baby%20Time%20Capsule/README.en.md) |

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
