# Challenges — Hack The Box

**English** | [🇪🇸 Español](README.md)

Index of solved challenges plus a category map to pick the next one. Each challenge has its own folder with `README.md` and `README.en.md`; unsolved ones get added once finished.

## Solved

| Challenge | Type | Difficulty | Technique | State | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM in `session.upload_progress`, use-after-free, ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [ES](Dark%20Embargo/README.md) | [Ver](Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | MD5 against the clock: session handling, regex, hashing in a script | **Retired** | [ES](Emdee%20five%20for%20life/README.md) | [Ver](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | LDAP injection: `*` as user and password, wildcards in search | **Retired** | [ES](Phonebook/README.md) | [Ver](Phonebook/README.en.md) |
| Under Construction | Web | Easy | JWT algorithm confusion: HS256 signed with the public key | **Retired** | [ES](Under%20Construction/README.md) | [Ver](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | Deserializacion PHP en cookie: `__destruct` escribe un webshell | Retired | [ES](Toxic/README.md) | [Ver](Toxic/README.en.md) |
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
