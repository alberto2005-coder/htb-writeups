# Retos — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Índice de retos resueltos y mapa de categorías para elegir el siguiente. Cada reto tiene su carpeta con `README.md` y `README.en.md`; los no resueltos se añaden al terminarlos.

## Resueltos

| Reto | Tipo | Dificultad | Técnica | Estado | ES | EN |
|---|---|---|---|---|---|---|
| Marshal in the Middle | Forensics | Medium | Logs de Zeek, descifrado TLS y exfiltración HTTP | **Retired** | [Ver](Marshal%20in%20the%20Middle/README.md) | [EN](Marshal%20in%20the%20Middle/README.en.md) |
| Lernaean | Web | Easy | Hydra, contraseña débil y redirect JavaScript evitable | **Retired** | [Ver](Lernaean/README.md) | [EN](Lernaean/README.en.md) |
| Kryptor | Pwn | Insane | Kernel 5.9.10: DirtyPipe (CVE-2022-0847) sobre la entry de busybox y disparo por `modprobe` | **Retired** | [Ver](Kryptor/README.md) | [EN](Kryptor/README.en.md) |
| Oldbridge | Pwn | Medium | Canario por fuerza bruta (`fork`), fuga de PIE y pivot `leave; ret` a ret2libc | **Retired** | [Ver](Oldbridge/README.md) | [EN](Oldbridge/README.en.md) |
| Space Pirate: Entrypoint | Pwn | Very Easy | Format string en `printf(local_38)`: `%7$hn` convierte `0xdeadbeef` en `0xdead1337` | **Retired** | [Ver](Space%20Pirate%20Entrypoint/README.md) | [EN](Space%20Pirate%20Entrypoint/README.en.md) |
| Space Pirate: Going Deeper | Pwn | Very Easy | Desbordamiento de 1 byte sin PIE: 56 de relleno y `\x01` al retorno | **Retired** | [Ver](Space%20Pirate%20Going%20Deeper/README.md) | [EN](Space%20Pirate%20Going%20Deeper/README.en.md) |
| Vault-breaker | Pwn | Very Easy | `strcpy` trunca la clave en el primer nulo; longitudes 31→0 dejan el XOR a cero | **Retired** | [Ver](Vault-breaker/README.md) | [EN](Vault-breaker/README.en.md) |
| ropme | Pwn | Hard | Ret2libc con leak de `puts@got`: base de libc y `system("/bin/sh")` | **Retired** | [Ver](ropme/README.md) | [EN](ropme/README.en.md) |
| Easy Phish | OSINT | Very Easy | SPF con `?all` y DMARC `p=none` en el dominio legítimo | **Retired** | [Ver](Easy%20Phish/README.md) | [EN](Easy%20Phish/README.en.md) |
| Hidden in Colors | Stego | Hard | Colores hex del PNG: el dato está en el valor de color, no en el LSB | **Retired** | [Ver](Hidden%20in%20Colors/README.md) | [EN](Hidden%20in%20Colors/README.en.md) |
| Bare Metal | Hardware | Easy | UART a 3.3 V, U-Boot y extracción del rootfs con `binwalk` | **Retired** | [Ver](Bare%20Metal/README.md) | [EN](Bare%20Metal/README.en.md) |
| Cryptohorrific | Mobile | Easy | App iOS: blob base64 en el plist y clave AES en el binario Mach-O | **Retired** | [Ver](Cryptohorrific/README.md) | [EN](Cryptohorrific/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM en `session.upload_progress`, use-after-free, leak de ASLR por `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [Ver](Dark%20Embargo/README.md) | [EN](Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | MD5 contra reloj: sesión, regex y cálculo del hash en un script | **Retired** | [Ver](Emdee%20five%20for%20life/README.md) | [EN](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | Inyección LDAP ciega: el flag es la contraseña de `reese`, no el bypass `*` | **Retired** | [Ver](Phonebook/README.md) | [EN](Phonebook/README.en.md) |
| Under Construction | Web | Easy | JWT `alg` confusion RS256→HS256 firmando con `/public.pem` | **Retired** | [Ver](Under%20Construction/README.md) | [EN](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | Deserialización PHP en la cookie → `PageModel::__destruct` → LFI + log poisoning | **Retired** | [Ver](Toxic/README.md) | [EN](Toxic/README.en.md) |
| LoveTok | Web | Easy | `eval` sobre el formato de fecha; `addslashes` no frena `${}` | **Retired** | [Ver](LoveTok/README.md) | [EN](LoveTok/README.en.md) |
| Templated | Web | Easy | SSTI de Jinja2 en `/<nombre>`: `{{7*7}}` → 49 y RCE por `__globals__` | **Retired** | [Ver](Templated/README.md) | [EN](Templated/README.en.md) |
| baby ninja jinja | Web | Easy | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | **Retired** | [Ver](baby%20ninja%20jinja/README.md) | [EN](baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Very Easy | SSTI de Mako vía `font4`: `${self.module.cache.util.os.popen(...).read()}` | **Retired** | [Ver](Spookifier/README.md) | [EN](Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Bundle JS con endpoints ocultos; comando secreto por API | **Retired** | [Ver](Flag%20Command/README.md) | [EN](Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | SSTI de Velocity: `#set` y reflexión de Java | **Retired** | [Ver](Labyrinth%20Linguist/README.md) | [EN](Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Contaminación de prototipos en Node hasta `child_process` | **Retired** | [Ver](breaking%20grad/README.md) | [EN](breaking%20grad/README.en.md) |
| Weather App | Web | Easy | SSRF con *response splitting* y SQLi en el servicio interno hasta la toma de la cuenta admin | **Retired** | [Ver](Weather%20App/README.md) | [EN](Weather%20App/README.en.md) |
| Freelancer | Web | Easy | SQLi en `portfolio.php?id=` y panel `/admin` hallado por fuzzing | **Retired** | [Ver](Freelancer/README.md) | [EN](Freelancer/README.en.md) |
| Passman | Web | Easy | GraphQL: `UpdatePassword` sin autorización; el flag está en el gestor del admin | **Retired** | [Ver](Passman/README.md) | [EN](Passman/README.en.md) |
| Cartographer | Web | Easy | SQLi en el login y `panel.php?info=flag` | **Retired** | [Ver](Cartographer/README.md) | [EN](Cartographer/README.en.md) |
| Dynastic | Crypto | Very Easy | Cifrado de Trithemius: el desplazamiento es el índice | **Retired** | [Ver](Dynastic/README.md) | [EN](Dynastic/README.en.md) |
| Makeshift | Crypto | Very Easy | Inversión y permutación de bloques de tres | **Retired** | [Ver](Makeshift/README.md) | [EN](Makeshift/README.en.md) |
| Primary Knowledge | Crypto | Very Easy | RSA con `n` primo: `φ(n) = n − 1`, sin factorizar nada | **Retired** | [Ver](Primary%20Knowledge/README.md) | [EN](Primary%20Knowledge/README.en.md) |
| Iced Tea | Crypto | Easy | TEA de 32 rondas con `delta` y máscara de 32 bits | **Retired** | [Ver](Iced%20Tea/README.md) | [EN](Iced%20Tea/README.en.md) |
| Illumination | Forensics | Easy | `.git` filtrado: el token sigue en el historial y en base64 | **Retired** | [Ver](Illumination/README.md) | [EN](Illumination/README.en.md) |
| MarketDump | Forensics | Easy | Exportar objetos HTTP y decodificar el outlier en base58 | **Retired** | [Ver](MarketDump/README.md) | [EN](MarketDump/README.en.md) |
| Took the Byte | Forensics | Easy | XOR de un byte (`0xFF`) sobre `password` → ZIP con `password.txt` | **Retired** | [Ver](Took%20the%20Byte/README.md) | [EN](Took%20the%20Byte/README.en.md) |
| Deadly Arthropod | Forensics | Medium | Reconstruir pulsaciones desde informes HID de un teclado USB | **Retired** | [Ver](Deadly%20Arthropod/README.md) | [EN](Deadly%20Arthropod/README.en.md) |
| Obscure | Forensics | Easy | Webshell ofuscado, PCAP con comandos y `.kdbx` crackeado con john | **Retired** | [Ver](Obscure/README.md) | [EN](Obscure/README.en.md) |
| Keep Tryin' | Forensics | Medium | Exfiltración por DNS en base64url y RC4 con clave débil | **Retired** | [Ver](Keep%20Tryin'/README.md) | [EN](Keep%20Tryin'/README.en.md) |
| Alien Cradle | Forensics | Very Easy | Desofuscar un *download cradle* de PowerShell por concatenación | **Retired** | [Ver](Alien%20Cradle/README.md) | [EN](Alien%20Cradle/README.en.md) |
| Extraterrestrial Persistence | Forensics | Very Easy | Unidad systemd en base64 como mecanismo de persistencia | **Retired** | [Ver](Extraterrestrial%20Persistence/README.md) | [EN](Extraterrestrial%20Persistence/README.en.md) |
| Plaintext Tleasure | Forensics | Very Easy | PCAP con HTTP en claro: credenciales y transferencia legibles sin descifrar | **Retired** | [Ver](Plaintext%20Tleasure/README.md) | [EN](Plaintext%20Tleasure/README.en.md) |
| Urgent | Forensics | Very Easy | `.eml` de phishing: MIME en base64/quoted-printable, URL encoding y adjunto VBS | **Retired** | [Ver](Urgent/README.md) | [EN](Urgent/README.en.md) |
| BabyEncryption | Crypto | Very Easy | Función afín módulo 256 e inverso modular | **Retired** | [Ver](BabyEncryption/README.md) | [EN](BabyEncryption/README.en.md) |
| Ancient Encodings | Crypto | Very Easy | Base64 dentro de hexadecimal, sin clave | **Retired** | [Ver](Ancient%20Encodings/README.md) | [EN](Ancient%20Encodings/README.en.md) |
| SpookyPass | Reversing | Very Easy | ELF con la contraseña y la flag en `.rodata`; la flag en UTF-32 (`strings -e l`) | **Retired** | [Ver](SpookyPass/README.md) | [EN](SpookyPass/README.en.md) |
| KORP Terminal | Web | Very Easy | SQLi con error visible y hash bcrypt crackeado | **Retired** | [Ver](KORP%20Terminal/README.md) | [EN](KORP%20Terminal/README.en.md) |
| TimeKORP | Web | Very Easy | Inyección de comandos en `date` vía `format`: `%H:%M:%S' \|cat /flag #` | **Retired** | [Ver](TimeKORP/README.md) | [EN](TimeKORP/README.en.md) |
| Behind the Scenes | Reversing | Very Easy | `UD2` como anti-descompilación y cuatro `strncmp` en GDB | **Retired** | [Ver](Behind%20the%20Scenes/README.md) | [EN](Behind%20the%20Scenes/README.en.md) |
| OnlyHacks | Web | Very Easy | IDOR en `/chat?rid=3`: el flag está en el chat de otro usuario (el XSS al bot es alternativa) | **Retired** | [Ver](OnlyHacks/README.md) | [EN](OnlyHacks/README.en.md) |
| Perfect Synchronization | Crypto | Easy | Sustitución por carácter (`char + 15`): análisis de frecuencias, no AES-ECB | **Retired** | [Ver](Perfect%20Synchronization/README.md) | [EN](Perfect%20Synchronization/README.en.md) |
| xorxorxor | Crypto | Easy | XOR con clave repetida y prefijo conocido | **Retired** | [Ver](xorxorxor/README.md) | [EN](xorxorxor/README.en.md) |
| Baby Time Capsule | Crypto | Very Easy | RSA con módulos pequeños: factorizar y descifrar | **Retired** | [Ver](Baby%20Time%20Capsule/README.md) | [EN](Baby%20Time%20Capsule/README.en.md) |
| Gunship | Web | Easy | Prototype pollution en `flat@5.0.0` + AST injection en el motor de plantillas | **Retired** | [Ver](Gunship/README.md) | [EN](Gunship/README.en.md) |
| baby interdimensional internet | Web | Easy | `exec()` de Python 2 sobre `ingredient`/`measurements`, sin filtros | **Retired** | [Ver](baby%20interdimensional%20internet/README.md) | [EN](baby%20interdimensional%20internet/README.en.md) |
| Interdimensional Internet | Web | Medium | WAF de `[ ( _ .` evadido con `\x` y exfiltración por `flask.session` | **Retired** | [Ver](Interdimensional%20Internet/README.md) | [EN](Interdimensional%20Internet/README.en.md) |
| Fake Boost | Forensics | Easy | PowerShell invertido + base64 y exfiltración AES en un `POST` | **Retired** | [Ver](Fake%20Boost/README.md) | [EN](Fake%20Boost/README.en.md) |
| Impossible Password | Reversing | Easy | Segundo `strcmp` contra `rand()`: igualar `$rdi`/`$rsi` en gdb | **Retired** | [Ver](Impossible%20Password/README.md) | [EN](Impossible%20Password/README.en.md) |
| Reg | Pwn | Easy | `gets()` en `run()`: offset `0x38` y ret2win a `winner()` sin PIE | **Retired** | [Ver](Reg/README.md) | [EN](Reg/README.en.md) |
| Survival of the Fittest | Blockchain | Very Easy | `strongAttack(20)` y `loot()` sin control del estado | **Retired** | [Ver](Survival%20of%20the%20Fittest/README.md) | [EN](Survival%20of%20the%20Fittest/README.en.md) |
| APKrypt | Mobile | Easy | Clave AES y blob en el APK, modo ECB | **Retired** | [Ver](APKrypt/README.md) | [EN](APKrypt/README.en.md) |
| Photon Lockdown | Hardware | Very Easy | SquashFS con la contraseña de fábrica en `config_default.xml` | **Retired** | [Ver](Photon%20Lockdown/README.md) | [EN](Photon%20Lockdown/README.en.md) |
| Prometheon | AI/ML | Medium | Inyección de prompt en cinco niveles encadenados | **Retired** | [Ver](Prometheon/README.md) | [EN](Prometheon/README.en.md) |
| Forks and Knives | Pwn | Medium | Off-by-one, format string, canario por `fork()` y ROP con `dup2` | **Retired** | [Ver](Forks%20and%20Knives/README.md) | [EN](Forks%20and%20Knives/README.en.md) |
| Evaluative | Coding | Very Easy | Polinomio de grado 8 y nueve coeficientes: Horner sin potencias | **Retired** | [Ver](Evaluative/README.md) | [EN](Evaluative/README.en.md) |
| Oddly Even | Coding | Very Easy | Paridad con `% 2`; cuidado con negativos en C | **Retired** | [Ver](Oddly%20Even/README.md) | [EN](Oddly%20Even/README.en.md) |
| Threat Index | Coding | Very Easy | 18 palabras con peso 1-18; `count` por término | **Retired** | [Ver](Threat%20Index/README.md) | [EN](Threat%20Index/README.en.md) |
| Watch Tower | ICS | Very Easy | PCAP Modbus/TCP: la flag está en los `reference numbers` de la función 16 | **Retired** | [Ver](Watch%20Tower/README.md) | [EN](Watch%20Tower/README.en.md) |
| Intrusion | ICS | Easy | Holding registers con `unit id` 52 y lectura automatizada con `umodbus`/`pymodbus` | **Retired** | [Ver](Intrusion/README.md) | [EN](Intrusion/README.en.md) |
| Factory | ICS | Easy | Lógica de escalera: modo manual y `Write Single Coil` para vaciar el tanque | **Retired** | [Ver](Factory/README.md) | [EN](Factory/README.en.md) |
| Shush Protocol | ICS | Very Easy | Función Modbus 102 propietaria: usuario y contraseña en claro en el flujo TCP | **Retired** | [Ver](Shush%20Protocol/README.md) | [EN](Shush%20Protocol/README.en.md) |
| Sneak peek | ICS | Easy | Función `0x64`: reescribir el MD5 de la contraseña en el bloque de memoria | **Retired** | [Ver](Sneak%20peek/README.md) | [EN](Sneak%20peek/README.en.md) |
| FlagCasino | Reversing | Very Easy | `srand` por carácter contra un array `check`: fuerza bruta de las 95 semillas imprimibles | **Retired** | [Ver](FlagCasino/README.md) | [EN](FlagCasino/README.en.md) |
| Simple Encryptor | Reversing | Very Easy | Semilla de tiempo en los 4 primeros bytes; XOR con `rand()` y rotación a la izquierda | **Retired** | [Ver](Simple%20Encryptor/README.md) | [EN](Simple%20Encryptor/README.en.md) |
| Shattered Tablet | Reversing | Very Easy | 40 comparaciones por índice en Ghidra: reasignar el buffer a `char[64]` | **Retired** | [Ver](Shattered%20Tablet/README.md) | [EN](Shattered%20Tablet/README.en.md) |
| Tear or Dear | Reversing | Medium | .NET WinForms con dnSpy de 32 bits: breakpoint en la comparación de credenciales | **Retired** | [Ver](Tear%20or%20Dear/README.md) | [EN](Tear%20or%20Dear/README.en.md) |
| Snakecode | Reversing | Easy | `.pyc` de Python 2.7 con `marshal` + zlib; la manzana del Snake escribe la flag | **Retired** | [Ver](Snakecode/README.md) | [EN](Snakecode/README.en.md) |
| Locked Away | Misc | Easy | PyJail: `blacklist.clear()` esquiva los corchetes y luego `open_chest()` | **Retired** | [Ver](Locked%20Away/README.md) | [EN](Locked%20Away/README.en.md) |
| Hidden Path | Misc | Easy | Variable `U+3164` (HANGUL FILLER) en el array de comandos: `choice=6` ejecuta la orden inyectada | **Retired** | [Ver](Hidden%20Path/README.md) | [EN](Hidden%20Path/README.en.md) |
| Aptitude Test | Misc | Very Easy | Cuestionario por `nc`: diez respuestas y el rol con la flag | **Retired** | [Ver](Aptitude%20Test/README.md) | [EN](Aptitude%20Test/README.en.md) |
| Chrono Mind | Misc | Easy | Path traversal `../config.py` como contexto del modelo y RCE por autocompletado | **Retired** | [Ver](Chrono%20Mind/README.md) | [EN](Chrono%20Mind/README.en.md) |
| Super-Duper Pwn | Misc | Easy | Bot de Discord, plantilla de `/checkout` y bypass de `vm2` con `Symbol.species` | **Retired** | [Ver](Super-Duper%20Pwn/README.md) | [EN](Super-Duper%20Pwn/README.en.md) |
| The Suspicious Reviewer | OSINT | Very Easy | Perfil público: About y metadatos de commits para el correo | **Retired** | [Ver](The%20Suspicious%20Reviewer/README.md) | [EN](The%20Suspicious%20Reviewer/README.en.md) |
| BitsNBytes | Stego | Hard | Dos PNG, StegSolve `SUB`, bits en una línea y Base64 | **Retired** | [Ver](BitsNBytes/README.md) | [EN](BitsNBytes/README.en.md) |
| Call | Crypto | Unknown | Audio DTMF y sustitución por números primos | **Retired** | [Ver](Call/README.md) | [EN](Call/README.en.md) |
| HDC | Web | Easy | Credenciales Base64 en JavaScript, bypass cliente y correo | **Retired** | [Ver](HDC/README.md) | [EN](HDC/README.en.md) |
| Weak RSA | Crypto | Very Easy | Módulo RSA débil o Wiener: recuperar la clave y descifrar `flag.enc` | **Retired** | [Ver](Weak%20RSA/README.md) | [EN](Weak%20RSA/README.en.md) |
| Baby Crypt | Reversing | Easy | XOR de 26 bytes con clave de 3 bytes y known plaintext del prefijo de flag | **Retired** | [Ver](Baby%20Crypt/README.md) | [EN](Baby%20Crypt/README.en.md) |
| Insider | Forensics | Easy | Perfil de Firefox: `logins.json` + `key4.db` y descifrado con `firepwd` | **Retired** | [Ver](Insider/README.md) | [EN](Insider/README.en.md) |
| Missing in Action | OSINT | Easy | LinkedIn → Twitter → Foursquare y dorks con nombre y empresa | **Retired** | [Ver](Missing%20in%20Action/README.md) | [EN](Missing%20in%20Action/README.en.md) |
| Spooky Time | Pwn | Medium | Format string en offset 8, fugas de PIE/libc y overwrite de `puts@got` | **Retired** | [Ver](Spooky%20Time/README.md) | [EN](Spooky%20Time/README.en.md) |

## Categorías

Los retos de HTB se agrupan en catorce categorías. Los números son orientativos y sirven para planificar, no como inventario exacto.

| Categoría | Aprox. | Qué se practica | Nota |
|---|---|---|---|
| Web | 75+ | XSS, SQLi, SSTI, SSRF, deserialización, JWT | La más rentable para empezar |
| Crypto | 93+ | RSA, AES, ECC, padding oracle, cifrados propios | Mucha matemática, poco tooling |
| Pwn | 61+ | Stack/heap, ROP, format string, UAF | Requiere binarios y depurador |
| Reversing | 44+ | x86/x64, ARM, .NET, Java, ofuscación | Combinar con Ghidra/IDA |
| Misc | 35+ | scripting, lógica, PyJail, encoding | Muy variado |
| Forensics | 33+ | memoria, disco, red, logs | Encaja con Sherlocks |
| OSINT | 12+ | geolocalización, redes, metadatos | Sin laboratorio |
| Stego | 12+ | LSB, steghide, audio, imágenes | Rápido de entrenar |
| Hardware | 11+ | UART, SPI, I2C, firmware | Requiere material o emulación |
| Mobile | 10+ | APK, Frida, smali, root detection | Android Studio |
| Blockchain | 10+ | Solidity, contratos, DeFi | Foundry/Remix |
| AI/ML | 5+ | adversarial ML, prompt injection | La más nueva |
| Coding | 6+ | entrada/salida, matemáticas, cadenas, backtracking | Sin binarios: solo stdin/stdout |
| ICS | 11+ | Modbus, OPC UA, S7comm, HMI/PLC | Categoría propia desde 2026; varios retos también se etiquetan Hardware |

## Convenciones

- Un directorio por reto, con el nombre del reto tal cual aparece en HTB.
- `README.md` en español y `README.en.md` en inglés, con front-matter (`challenge`, `type`, `difficulty`, `state`, `tags`).
- Sin flags: la evidencia se recorta y se redacta.
- Si el reto trae código o binario, se guarda junto al writeup solo si es redistribuible.

## Plantilla

`templates/challenge-template.md` y `templates/challenge-template.en.md`.

## Sherlocks

Los escenarios de investigación defensiva no son retos de ataque y viven aparte: [sherlocks/README.md](../sherlocks/README.md) · [EN](../sherlocks/README.en.md).
