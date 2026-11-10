# Retos — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Índice de retos resueltos y mapa de categorías para elegir el siguiente. Cada reto tiene su carpeta con `README.md` y `README.en.md`; los no resueltos se añaden al terminarlos.

## Resueltos

| Reto | Tipo | Dificultad | Técnica | Estado | ES | EN |
|---|---|---|---|---|---|---|
| ropme | Pwn | Easy | Ret2libc con leak de `puts@got`: base de libc y `system("/bin/sh")` | **Retired** | [Ver](ropme/README.md) | [EN](ropme/README.en.md) |
| Easy Phish | OSINT | Very Easy | SPF con `?all` y DMARC `p=none` en el dominio legítimo | **Retired** | [Ver](Easy%20Phish/README.md) | [EN](Easy%20Phish/README.en.md) |
| Hidden in Colors | Stego | Easy | LSB en PNG con `zsteg` y lectura por canales | **Retired** | [Ver](Hidden%20in%20Colors/README.md) | [EN](Hidden%20in%20Colors/README.en.md) |
| Bare Metal | Hardware | Easy | UART a 3.3 V, U-Boot y extracción del rootfs con `binwalk` | **Retired** | [Ver](Bare%20Metal/README.md) | [EN](Bare%20Metal/README.en.md) |
| Cryptohorrific | Mobile | Easy | App iOS: blob base64 en el plist y clave AES en el binario Mach-O | **Retired** | [Ver](Cryptohorrific/README.md) | [EN](Cryptohorrific/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM en `session.upload_progress`, use-after-free, leak de ASLR por `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [Ver](Dark%20Embargo/README.md) | [EN](Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | MD5 contra reloj: sesión, regex y cálculo del hash en un script | **Retired** | [Ver](Emdee%20five%20for%20life/README.md) | [EN](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | Inyección LDAP: `*` en usuario y contraseña, y buscador con comodines | **Retired** | [Ver](Phonebook/README.md) | [EN](Phonebook/README.en.md) |
| Under Construction | Web | Easy | Confusión de algoritmos JWT: HS256 firmado con la clave pública | **Retired** | [Ver](Under%20Construction/README.md) | [EN](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | Inyeccion de objetos PHP: `PageModel::__destruct` incluye un fichero (LFI) y log poisoning en nginx | **Retired** | [Ver](Toxic/README.md) | [EN](Toxic/README.en.md) |
| LoveTok | Web | Easy | `eval` sobre el formato de fecha; `addslashes` no frena `${}` | **Retired** | [Ver](LoveTok/README.md) | [EN](LoveTok/README.en.md) |
| Templated | Web | Easy | SSTI de Jinja2 en `render_template_string` | **Retired** | [Ver](Templated/README.md) | [EN](Templated/README.en.md) |
| baby ninja jinja | Web | Easy | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | **Retired** | [Ver](baby%20ninja%20jinja/README.md) | [EN](baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Easy | SSTI de Mako: `self.module` hasta `os` | **Retired** | [Ver](Spookifier/README.md) | [EN](Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Bundle JS con endpoints ocultos; comando secreto por API | **Retired** | [Ver](Flag%20Command/README.md) | [EN](Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | SSTI de Velocity: `#set` y reflexión de Java | **Retired** | [Ver](Labyrinth%20Linguist/README.md) | [EN](Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Contaminación de prototipos en Node hasta `child_process` | **Retired** | [Ver](breaking%20grad/README.md) | [EN](breaking%20grad/README.en.md) |
| Weather App | Web | Easy | SSRF con *response splitting* y SQLi en el servicio interno hasta la toma de la cuenta admin | **Retired** | [Ver](Weather%20App/README.md) | [EN](Weather%20App/README.en.md) |
| Freelancer | Web | Easy | SQLi en el login y `UNION SELECT` para extraer la flag | **Retired** | [Ver](Freelancer/README.md) | [EN](Freelancer/README.en.md) |
| Passman | Web | Easy | GraphQL con IDOR en `UpdatePassword`: cambio de la contraseña del admin | **Retired** | [Ver](Passman/README.md) | [EN](Passman/README.en.md) |
| Cartographer | Web | Easy | SQLi en el login y `panel.php?info=flag` | **Retired** | [Ver](Cartographer/README.md) | [EN](Cartographer/README.en.md) |
| Dynastic | Crypto | Very Easy | Cifrado de Trithemius: el desplazamiento es el índice | **Retired** | [Ver](Dynastic/README.md) | [EN](Dynastic/README.en.md) |
| Makeshift | Crypto | Very Easy | Inversión y permutación de bloques de tres | **Retired** | [Ver](Makeshift/README.md) | [EN](Makeshift/README.en.md) |
| Primary Knowledge | Crypto | Very Easy | RSA con `n` primo → φ = n − 1 | **Retired** | [Ver](Primary%20Knowledge/README.md) | [EN](Primary%20Knowledge/README.en.md) |
| Iced Tea | Crypto | Easy | TEA de 32 rondas con `delta` y máscara de 32 bits | **Retired** | [Ver](Iced%20Tea/README.md) | [EN](Iced%20Tea/README.en.md) |
| Illumination | Forensics | Easy | `.git` filtrado: el token sigue en el historial y en base64 | **Retired** | [Ver](Illumination/README.md) | [EN](Illumination/README.en.md) |
| MarketDump | Forensics | Easy | Exportar objetos HTTP y decodificar el outlier en base58 | **Retired** | [Ver](MarketDump/README.md) | [EN](MarketDump/README.en.md) |
| Took the Byte | Forensics | Easy | XOR de un byte (`0xFF`) hasta un ZIP con el fichero de contraseña | **Retired** | [Ver](Took%20the%20Byte/README.md) | [EN](Took%20the%20Byte/README.en.md) |
| Deadly Arthropod | Forensics | Medium | Reconstruir pulsaciones desde informes HID de un teclado USB | **Retired** | [Ver](Deadly%20Arthropod/README.md) | [EN](Deadly%20Arthropod/README.en.md) |
| Obscure | Forensics | Easy | Webshell ofuscado, PCAP con comandos y `.kdbx` crackeado con john | **Retired** | [Ver](Obscure/README.md) | [EN](Obscure/README.en.md) |
| Keep Tryin' | Forensics | Medium | Exfiltración por DNS en base64url y RC4 con clave débil | **Retired** | [Ver](Keep%20Tryin'/README.md) | [EN](Keep%20Tryin'/README.en.md) |
| Alien Cradle | Forensics | Very Easy | Desofuscar un *download cradle* de PowerShell por concatenación | **Retired** | [Ver](Alien%20Cradle/README.md) | [EN](Alien%20Cradle/README.en.md) |
| Extraterrestrial Persistence | Forensics | Very Easy | Unidad systemd en base64 como mecanismo de persistencia | **Retired** | [Ver](Extraterrestrial%20Persistence/README.md) | [EN](Extraterrestrial%20Persistence/README.en.md) |
| Plaintext Tleasure | Forensics | Very Easy | HTTP sin cifrar: credenciales y flag en el flujo | **Retired** | [Ver](Plaintext%20Tleasure/README.md) | [EN](Plaintext%20Tleasure/README.en.md) |
| Urgent | Forensics | Very Easy | Correo de phishing: base64, URL encoding y adjunto VBScript | **Retired** | [Ver](Urgent/README.md) | [EN](Urgent/README.en.md) |
| BabyEncryption | Crypto | Very Easy | Función afín módulo 256 e inverso modular | **Retired** | [Ver](BabyEncryption/README.md) | [EN](BabyEncryption/README.en.md) |
| Ancient Encodings | Crypto | Very Easy | Base64 dentro de hexadecimal, sin clave | **Retired** | [Ver](Ancient%20Encodings/README.md) | [EN](Ancient%20Encodings/README.en.md) |
| SpookyPass | Reversing | Very Easy | Contraseña en claro en las cadenas del ELF | **Retired** | [Ver](SpookyPass/README.md) | [EN](SpookyPass/README.en.md) |
| KORP Terminal | Web | Very Easy | SQLi con error visible y hash bcrypt crackeado | **Retired** | [Ver](KORP%20Terminal/README.md) | [EN](KORP%20Terminal/README.en.md) |
| TimeKORP | Web | Very Easy | Inyección de comandos a través del formato de la hora | **Retired** | [Ver](TimeKORP/README.md) | [EN](TimeKORP/README.en.md) |
| Behind the Scenes | Reversing | Very Easy | `UD2` como anti-descompilación y cuatro `strncmp` en GDB | **Retired** | [Ver](Behind%20the%20Scenes/README.md) | [EN](Behind%20the%20Scenes/README.en.md) |
| OnlyHacks | Web | Very Easy | XSS almacenado contra un bot para robar la cookie de sesión | **Retired** | [Ver](OnlyHacks/README.md) | [EN](OnlyHacks/README.en.md) |
| Perfect Synchronization | Crypto | Easy | AES-ECB y análisis de frecuencias por bloques | **Retired** | [Ver](Perfect%20Synchronization/README.md) | [EN](Perfect%20Synchronization/README.en.md) |
| xorxorxor | Crypto | Easy | XOR con clave repetida y prefijo conocido | **Retired** | [Ver](xorxorxor/README.md) | [EN](xorxorxor/README.en.md) |
| Baby Time Capsule | Crypto | Very Easy | RSA con módulos pequeños: factorizar y descifrar | **Retired** | [Ver](Baby%20Time%20Capsule/README.md) | [EN](Baby%20Time%20Capsule/README.en.md) |

## Categorías

Los retos de HTB se agrupan en doce categorías. Los números son orientativos y sirven para planificar, no como inventario exacto.

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

## Convenciones

- Un directorio por reto, con el nombre del reto tal cual aparece en HTB.
- `README.md` en español y `README.en.md` en inglés, con front-matter (`challenge`, `type`, `difficulty`, `state`, `tags`).
- Sin flags: la evidencia se recorta y se redacta.
- Si el reto trae código o binario, se guarda junto al writeup solo si es redistribuible.

## Plantilla

`templates/challenge-template.md` y `templates/challenge-template.en.md`.

## Sherlocks

Los escenarios de investigación defensiva no son retos de ataque y viven aparte: [sherlocks/README.md](../sherlocks/README.md) · [EN](../sherlocks/README.en.md).
