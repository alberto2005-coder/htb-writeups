# Challenges — Hack The Box

**English** | [🇪🇸 Español](README.md)

Index of solved challenges plus a category map to pick the next one. Each challenge has its own folder with `README.md` and `README.en.md`; unsolved ones get added once finished.

## Solved

| Challenge | Type | Difficulty | Technique | State | ES | EN |
|---|---|---|---|---|---|---|
| ropme | Pwn | Hard | Ret2libc with a `puts@got` leak: libc base and `system("/bin/sh")` | **Retired** | [ES](ropme/README.md) | [Ver](ropme/README.en.md) |
| Easy Phish | OSINT | Very Easy | `?all` SPF and `p=none` DMARC on the legitimate domain | **Retired** | [ES](Easy%20Phish/README.md) | [Ver](Easy%20Phish/README.en.md) |
| Hidden in Colors | Stego | Hard | PNG hex colours: the data lives in the colour value, not the LSB | **Retired** | [ES](Hidden%20in%20Colors/README.md) | [Ver](Hidden%20in%20Colors/README.en.md) |
| Bare Metal | Hardware | Easy | 3.3 V UART, U-Boot and rootfs extraction with `binwalk` | **Retired** | [ES](Bare%20Metal/README.md) | [Ver](Bare%20Metal/README.en.md) |
| Cryptohorrific | Mobile | Easy | iOS app: base64 blob in the plist, AES key inside the Mach-O binary | **Retired** | [ES](Cryptohorrific/README.md) | [Ver](Cryptohorrific/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM in `session.upload_progress`, use-after-free, ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [ES](Dark%20Embargo/README.md) | [Ver](Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | MD5 against the clock: session handling, regex, hashing in a script | **Retired** | [ES](Emdee%20five%20for%20life/README.md) | [Ver](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | Blind LDAP injection: the flag is `reese`'s password, not the `*` bypass | **Retired** | [ES](Phonebook/README.md) | [Ver](Phonebook/README.en.md) |
| Under Construction | Web | Easy | JWT `alg` confusion RS256→HS256 signing with `/public.pem` | **Retired** | [ES](Under%20Construction/README.md) | [Ver](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | PHP deserialization in the cookie → `PageModel::__destruct` → LFI plus log poisoning | Retired | [ES](Toxic/README.md) | [Ver](Toxic/README.en.md) |
| LoveTok | Web | Easy | `eval` over the date format; `addslashes` does not stop `${}` | **Retired** | [ES](LoveTok/README.md) | [Ver](LoveTok/README.en.md) |
| Templated | Web | Easy | Jinja2 SSTI at `/<nombre>`: `{{7*7}}` → 49 and RCE via `__globals__` | Retired | [ES](Templated/README.md) | [Ver](Templated/README.en.md) |
| baby ninja jinja | Web | Easy | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | Retired | [ES](baby%20ninja%20jinja/README.md) | [Ver](baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Very Easy | Mako SSTI through `font4`: `${self.module.cache.util.os.popen(...).read()}` | Retired | [ES](Spookifier/README.md) | [Ver](Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Bundle JS con endpoints ocultos; comando secreto por API | Retired | [ES](Flag%20Command/README.md) | [Ver](Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | Velocity SSTI: `#set` plus Java reflection | **Retired** | [ES](Labyrinth%20Linguist/README.md) | [Ver](Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Contaminación de prototipos en Node hasta `child_process` | Retired | [ES](breaking%20grad/README.md) | [Ver](breaking%20grad/README.en.md) |
| Weather App | Web | Easy | SSRF with *response splitting* and SQLi in the internal service up to admin account takeover | **Retired** | [ES](Weather%20App/README.md) | [Ver](Weather%20App/README.en.md) |
| Freelancer | Web | Easy | SQLi in `portfolio.php?id=` and an `/admin` panel found by fuzzing | **Retired** | [ES](Freelancer/README.md) | [Ver](Freelancer/README.en.md) |
| Passman | Web | Easy | GraphQL: unauthenticated `UpdatePassword`; the flag lives in the admin's manager | **Retired** | [ES](Passman/README.md) | [Ver](Passman/README.en.md) |
| Cartographer | Web | Easy | SQLi in the login form and `panel.php?info=flag` | **Retired** | [ES](Cartographer/README.md) | [Ver](Cartographer/README.en.md) |
| Dynastic | Crypto | Very Easy | Trithemius cipher: the shift is the index | **Retired** | [ES](Dynastic/README.md) | [Ver](Dynastic/README.en.md) |
| Makeshift | Crypto | Very Easy | Reversal plus permutation of three-byte blocks | **Retired** | [ES](Makeshift/README.md) | [Ver](Makeshift/README.en.md) |
| Primary Knowledge | Crypto | Very Easy | RSA with a prime `n`: `φ(n) = n − 1`, no factorisation needed | **Retired** | [ES](Primary%20Knowledge/README.md) | [Ver](Primary%20Knowledge/README.en.md) |
| Iced Tea | Crypto | Easy | 32-round TEA with `delta` and a 32-bit mask | **Retired** | [ES](Iced%20Tea/README.md) | [Ver](Iced%20Tea/README.en.md) |
| Illumination | Forensics | Easy | Leaked `.git`: the token survives in history, base64-encoded | **Retired** | [ES](Illumination/README.md) | [Ver](Illumination/README.en.md) |
| MarketDump | Forensics | Easy | Export HTTP objects and decode the outlier as base58 | **Retired** | [ES](MarketDump/README.md) | [Ver](MarketDump/README.en.md) |
| Took the Byte | Forensics | Easy | Single-byte XOR (`0xFF`) over `password` → a ZIP with `password.txt` | **Retired** | [ES](Took%20the%20Byte/README.md) | [Ver](Took%20the%20Byte/README.en.md) |
| Deadly Arthropod | Forensics | Medium | Rebuild keystrokes from USB keyboard HID reports | **Retired** | [ES](Deadly%20Arthropod/README.md) | [Ver](Deadly%20Arthropod/README.en.md) |
| Obscure | Forensics | Easy | Obfuscated webshell, PCAP with commands and a `.kdbx` cracked with john | **Retired** | [ES](Obscure/README.md) | [Ver](Obscure/README.en.md) |
| Keep Tryin' | Forensics | Medium | DNS exfiltration in base64url and RC4 with a weak key | **Retired** | [ES](Keep%20Tryin'/README.md) | [Ver](Keep%20Tryin'/README.en.md) |
| Alien Cradle | Forensics | Very Easy | Deobfuscate a PowerShell download cradle built from string concatenation | **Retired** | [ES](Alien%20Cradle/README.md) | [Ver](Alien%20Cradle/README.en.md) |
| Extraterrestrial Persistence | Forensics | Very Easy | base64-encoded systemd unit as the persistence mechanism | **Retired** | [ES](Extraterrestrial%20Persistence/README.md) | [Ver](Extraterrestrial%20Persistence/README.en.md) |
| Plaintext Tleasure | Forensics | Very Easy | PCAP with cleartext HTTP: credentials and transfer readable without decryption | **Retired** | [ES](Plaintext%20Tleasure/README.md) | [Ver](Plaintext%20Tleasure/README.en.md) |
| Urgent | Forensics | Very Easy | Phishing `.eml`: base64/quoted-printable MIME, URL encoding and a VBS attachment | **Retired** | [ES](Urgent/README.md) | [Ver](Urgent/README.en.md) |
| BabyEncryption | Crypto | Very Easy | Affine map modulo 256 and the modular inverse | **Retired** | [ES](BabyEncryption/README.md) | [Ver](BabyEncryption/README.en.md) |
| Ancient Encodings | Crypto | Very Easy | Base64 inside hexadecimal, no key | **Retired** | [ES](Ancient%20Encodings/README.md) | [Ver](Ancient%20Encodings/README.en.md) |
| SpookyPass | Reversing | Very Easy | ELF with the password and flag in `.rodata`; the flag as UTF-32 (`strings -e l`) | **Retired** | [ES](SpookyPass/README.md) | [Ver](SpookyPass/README.en.md) |
| KORP Terminal | Web | Very Easy | Error-based SQLi and a cracked bcrypt hash | **Retired** | [ES](KORP%20Terminal/README.md) | [Ver](KORP%20Terminal/README.en.md) |
| TimeKORP | Web | Very Easy | Command injection into `date` through `format`: `%H:%M:%S' |cat /flag #` | **Retired** | [ES](TimeKORP/README.md) | [Ver](TimeKORP/README.en.md) |
| Behind the Scenes | Reversing | Very Easy | `UD2` anti-decompilation and four `strncmp` calls in GDB | **Retired** | [ES](Behind%20the%20Scenes/README.md) | [Ver](Behind%20the%20Scenes/README.en.md) |
| OnlyHacks | Web | Very Easy | IDOR at `/chat?rid=3`: the flag sits in another user's chat (the bot XSS is an alternative) | **Retired** | [ES](OnlyHacks/README.md) | [Ver](OnlyHacks/README.en.md) |
| Perfect Synchronization | Crypto | Easy | Per-character substitution (`char + 15`): frequency analysis, not AES-ECB | **Retired** | [ES](Perfect%20Synchronization/README.md) | [Ver](Perfect%20Synchronization/README.en.md) |
| xorxorxor | Crypto | Easy | Repeating-key XOR with a known prefix | **Retired** | [ES](xorxorxor/README.md) | [Ver](xorxorxor/README.en.md) |
| Baby Time Capsule | Crypto | Very Easy | RSA with small moduli: factor and decrypt | **Retired** | [ES](Baby%20Time%20Capsule/README.md) | [Ver](Baby%20Time%20Capsule/README.en.md) |
| Gunship | Web | Easy | Prototype pollution in `flat@5.0.0` + AST injection in the template engine | **Retired** | [ES](Gunship/README.md) | [Ver](Gunship/README.en.md) |
| baby interdimensional internet | Web | Easy | Python 2 `exec()` over `ingredient`/`measurements`, no filters | **Retired** | [ES](baby%20interdimensional%20internet/README.md) | [Ver](baby%20interdimensional%20internet/README.en.md) |
| Interdimensional Internet | Web | Medium | `[ ( _ .` WAF bypassed with `\x` and exfiltration via `flask.session` | **Retired** | [ES](Interdimensional%20Internet/README.md) | [Ver](Interdimensional%20Internet/README.en.md) |
| Fake Boost | Forensics | Easy | Reversed base64 PowerShell and AES exfiltration in a `POST` | **Retired** | [ES](Fake%20Boost/README.md) | [Ver](Fake%20Boost/README.en.md) |
| Impossible Password | Reversing | Easy | Second `strcmp` against `rand()`: equalise `$rdi`/`$rsi` in gdb | **Retired** | [ES](Impossible%20Password/README.md) | [Ver](Impossible%20Password/README.en.md) |
| Reg | Pwn | Easy | `gets()` in `run()`: `0x38` offset and ret2win into `winner()` with no PIE | **Retired** | [ES](Reg/README.md) | [Ver](Reg/README.en.md) |
| Survival of the Fittest | Blockchain | Very Easy | `strongAttack(20)` and `loot()` with no state check | **Retired** | [ES](Survival%20of%20the%20Fittest/README.md) | [Ver](Survival%20of%20the%20Fittest/README.en.md) |
| APKrypt | Mobile | Easy | AES key and blob inside the APK, ECB mode | **Retired** | [ES](APKrypt/README.md) | [Ver](APKrypt/README.en.md) |
| Photon Lockdown | Hardware | Very Easy | SquashFS with the factory password in `config_default.xml` | **Retired** | [ES](Photon%20Lockdown/README.md) | [Ver](Photon%20Lockdown/README.en.md) |
| Prometheon | AI/ML | Medium | Prompt injection across five chained levels | **Retired** | [ES](Prometheon/README.md) | [Ver](Prometheon/README.en.md) |
| Forks and Knives | Pwn | Medium | Off-by-one, format string, `fork()` canary and `dup2` ROP | **Retired** | [ES](Forks%20and%20Knives/README.md) | [Ver](Forks%20and%20Knives/README.en.md) |

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
