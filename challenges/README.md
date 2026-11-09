# Retos — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Índice de retos resueltos y mapa de categorías para elegir el siguiente. Cada reto tiene su carpeta con `README.md` y `README.en.md`; los no resueltos se añaden al terminarlos.

## Resueltos

| Reto | Tipo | Dificultad | Técnica | Estado | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | PHP 8.4.26: OOM en `session.upload_progress`, use-after-free, leak de ASLR por `Set-Cookie`, `pDestructor` → `system()` | **Retired** | [Ver](Dark%20Embargo/README.md) | [EN](Dark%20Embargo/README.en.md) |

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
