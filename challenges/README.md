# Retos — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Índice de retos resueltos y mapa de categorías para elegir el siguiente. Cada reto tiene su carpeta con `README.md` y `README.en.md`; los no resueltos se añaden al terminarlos.

## Resueltos

| Reto | Tipo | Dificultad | Técnica | Estado | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM en `session.upload_progress`, use-after-free, leak de ASLR por `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [Ver](Dark%20Embargo/README.md) | [EN](Dark%20Embargo/README.en.md) |
| Emdee five for life | Web | Easy | MD5 contra reloj: sesión, regex y cálculo del hash en un script | **Retired** | [Ver](Emdee%20five%20for%20life/README.md) | [EN](Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | Inyección LDAP: `*` en usuario y contraseña, y buscador con comodines | **Retired** | [Ver](Phonebook/README.md) | [EN](Phonebook/README.en.md) |
| Under Construction | Web | Easy | Confusión de algoritmos JWT: HS256 firmado con la clave pública | **Retired** | [Ver](Under%20Construction/README.md) | [EN](Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | Deserializacion PHP en cookie: `__destruct` escribe un webshell | **Retired** | [Ver](Toxic/README.md) | [EN](Toxic/README.en.md) |
| LoveTok | Web | Easy | `eval` sobre el formato de fecha; `addslashes` no frena `${}` | **Retired** | [Ver](LoveTok/README.md) | [EN](LoveTok/README.en.md) |
| Templated | Web | Easy | SSTI de Jinja2 en `render_template_string` | **Retired** | [Ver](Templated/README.md) | [EN](Templated/README.en.md) |
| baby ninja jinja | Web | Easy | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | **Retired** | [Ver](baby%20ninja%20jinja/README.md) | [EN](baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Easy | SSTI de Mako: `self.module` hasta `os` | **Retired** | [Ver](Spookifier/README.md) | [EN](Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Bundle JS con endpoints ocultos; comando secreto por API | **Retired** | [Ver](Flag%20Command/README.md) | [EN](Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | SSTI de Velocity: `#set` y reflexión de Java | **Retired** | [Ver](Labyrinth%20Linguist/README.md) | [EN](Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Contaminación de prototipos en Node hasta `child_process` | **Retired** | [Ver](breaking%20grad/README.md) | [EN](breaking%20grad/README.en.md) |
| Weather App | Web | Easy | SSRF contra un servicio interno en loopback | **Retired** | [Ver](Weather%20App/README.md) | [EN](Weather%20App/README.en.md) |
| Freelancer | Web | Easy | SQLi en el login y `UNION SELECT` para extraer la flag | **Retired** | [Ver](Freelancer/README.md) | [EN](Freelancer/README.en.md) |

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
