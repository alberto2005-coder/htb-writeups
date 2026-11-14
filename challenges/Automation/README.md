---
challenge: Automation
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, powershell, obfuscation, base64]
---

# Automation — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un script de PowerShell ofuscado descarga y ejecuta una segunda etapa. Se decodifica base64, se reconstruyen las cadenas concatenadas y se sigue la URL hasta el payload que contiene la flag.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Se entrega un script o un artefacto de PowerShell.
- El enunciado menciona automatización.

```bash
file automation.ps1
head -40 automation.ps1
```

## Reconocimiento

- `-enc`/`-EncodedCommand`, `FromBase64String`, `IEX` y concatenación de cadenas.
- Variables con nombres aleatorios.
- Una URL o un blob adicional.

## Análisis del código

Se extrae el base64 y se decodifica como UTF-16LE. El resultado se desofusca sustituyendo variables y concatenaciones. La segunda etapa suele descargar un binario o ejecutar otra cadena.

```powershell
[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($blob))
```

## Explicación del fallo

La ofuscación no cifra: solo oculta. El flujo `DownloadString`/`IEX` permite reconstruir la cadena y obtener el payload sin ejecutarlo.

## Reproducción local

- Trabajar en una VM aislada y sin red.
- Deshabilitar la ejecución automática.
- Guardar cada etapa decodificada en archivos separados.
- Calcular hashes antes y después.

## Explotación

```bash
python3 decode.py automation.ps1
strings -a stage2.bin | grep -i flag
```

La flag aparece en el payload o en la salida; se redacta.

## Evidencia

- Blob base64 y script decodificado.
- Hashes de las etapas.
- URL/C2 redactados.

## Lecciones aprendidas

- `IEX` y `DownloadString` son indicadores claros.
- UTF-16LE es habitual en `EncodedCommand`.
- La desofuscación estática evita ejecutar malware.

## Mitigaciones y detección

- Habilitar Script Block Logging (4104) y AMSI.
- Restringir PowerShell y firmar scripts.
- Alertar de `-enc`, `IEX` y descargas desde PowerShell.

## Referencias

- <https://www.hackthebox.com/challenges/Automation>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/automation/>
- <https://attack.mitre.org/techniques/T1059/001/>
