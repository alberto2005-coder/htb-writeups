---
sherlock: Lockpick
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
evidence: Muestra de ransomware y ficheros cifrados
tools: [Detect It Easy, Ghidra, x64dbg, CyberChef]
state: Retired
tags: [dfir, análisis-de-malware]
---


# Lockpick — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Primer caso de la familia **Lockpick**: un ransomware ha cifrado datos de la empresa. Hay que analizar la muestra para entender cómo cifra, qué clave usa y cómo recuperar los ficheros sin pagar.

## Evidencias

- La muestra del binario y un conjunto de ficheros cifrados con su nota de rescate.

## Investigación

1. **Triage**: hash, tipo de fichero, compilador, si está empaquetado.

```bash
sha256sum sample; file sample
detect-it-easy sample
strings -n 8 sample | head -50
```

2. **Importaciones**: buscar `CryptAcquireContext`/`CryptEncrypt` (CryptoAPI), `BCrypt*`, o AES/RSA embebido. Un binario Go o .NET cambia el enfoque de análisis.

3. **Clave**: localizar cómo se genera o deriva. Lo habitual es AES con clave aleatoria por fichero y esa clave cifrada con una pública RSA; si la clave es simétrica y está embebida u ofuscada, se extrae.

4. **Descifrar**: reproducir la rutina con el algoritmo y el modo correctos y verificar con la cabecera del fichero original.

```python
from Crypto.Cipher import AES
# clave/IV extraídos; el modo y el padding deben coincidir con los del binario
```

5. **Documentar** los IOCs y el punto exacto del código donde se cifra.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- `strings` + importaciones resuelven la mitad del triage sin desensamblar.
- Recuperar datos es posible cuando la clave está embebida, no cuando es asimétrica y se borra.

## Tropiezos

- **Ejecutar la muestra**: usar siempre una VM aislada y sin red.
- **Modo y padding**: un AES-CBC con IV distinto produce basura; comprobar con el primer bloque.
- **Empaquetado**: si las cadenas son ruido, desempaquetar (UPX u otro) antes de analizar.
