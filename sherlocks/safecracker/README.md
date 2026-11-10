---
title: Safecracker
category: DFIR / Malware
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, malware, ransomware, pe, strings, xor]
sherlock: Safecracker
domain: Malware Analysis
---


# Safecracker — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Un usuario abre un fichero que parece legítimo y, minutos después, documentos con una extensión extraña quedan cifrados. La evidencia son el ejecutable, los ficheros afectados y artefactos del host. El objetivo es entender cómo cifra, con qué clave y qué se puede recuperar.

## Evidencias

```bash
sha256sum *; file *
strings -a -n 8 sample.exe | head -50
```

- **No ejecutar** la muestra fuera de una VM aislada y sin red.
- VirusTotal por hash (no por subida) para contexto de familia.
- `pefile`/PE-bear para imports, secciones y timestamp; `capa` para capacidades.
- Buscar la extensión de los ficheros cifrados y su tamaño: una diferencia de 16/32 bytes sugiere IV + bloque.

## Investigación

1. **Strings y recursos**: nombres de API (`CryptEncrypt`, `BCryptEncrypt`), rutas, extensión y notas de rescate.
2. **Análisis estático**: localizar la rutina de cifrado en Ghidra/IDA; identificar algoritmo (AES-CBC, XOR, RC4) por constantes (`S-box`, `delta`, tablas).
3. **Clave**: puede estar embebida, derivada de una contraseña o generada por `CryptGenRandom`. Si es embebida, se extrae del binario; si es aleatoria, se busca en memoria o en el fichero de clave.
4. **Verificación**: descifrar un fichero de prueba y comprobar cabecera (`%PDF`, `PK`, `\x89PNG`).
5. **Alcance**: contar ficheros afectados por extensión y por unidad; revisar `$MFT`/`UsnJrnl` para los renombrados.
6. **Evidencia de disco**: el paquete del Sherlock es un ZIP que se carga en **Autopsy** (no sólo el binario). De ahí salen la cuenta usada en el acceso inicial, los ficheros cifrados y la nota de rescate; la pregunta clave del análisis es **qué llamada al sistema borra los originales** tras cifrarlos (`NtSetInformationFile` con `FileDispositionInformation`).

## Conclusiones

```text
.doc  ->  .doc.<ext>
tamaño original + 16 bytes  ->  IV de 16 bytes + AES-CBC
strings: "README_DECRYPT.txt", "AES", "key"
```

La nota de rescate y la extensión confirman ransomware; el tamaño alineado a 16 confirma cifrado por bloques. En la evidencia de Autopsy, además, se ve que el binario **borra los originales** con `NtSetInformationFile` en lugar de `DeleteFile`, un detalle que explica por qué el triaje automático no lo detectó.

## Lecciones

- El hash y los metadatos del PE dicen más que el nombre del fichero.
- Un cifrado correcto no se rompe: se busca la clave en el binario, la memoria o un fallo de implementación (misma clave, IV fijo, XOR).
- La timeline de MFT explica qué se cifró y cuándo, incluso si el binario se borró.

- **Sysmon 11** (creación de ficheros con extensión nueva) y **1** (proceso desde `%TEMP%`/descargas).
- Copias de seguridad inmutables y offline; probar restauración.
- Bloquear ejecutables desde correo y aplicar ASR de Windows Defender.
- YARA por familia y por rutina de cifrado, no por hash.

MITRE: T1486, T1027, T1059.
