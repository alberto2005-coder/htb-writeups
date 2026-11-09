---
challenge: Keep Tryin'
category: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, dns-exfil, base64url, rc4]
---

# Keep Tryin' — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un PCAP de **26 paquetes** con tres cosas: un `POST /flag` con la palabra `TryHarder`, un `POST /lootz` con base64 («Keep trying, buffy») y **consultas DNS TXT con subdominios en base64url**. El nombre del primer subdominio decodifica a `secret.txt|1`: es una exfiltración por DNS. Los trozos se concatenan, se descifran con **RC4** usando `TryHarder` como clave y sale un ZIP con `secret.txt`.

## Evidencia

- `keeptryin.pcap` dentro de un ZIP.

## Método

1. **Ver el conjunto**: es tan pequeño que se lee entero.

```bash
tshark -r keeptryin.pcap -Y 'dns' -T fields -e dns.qry.name | head
```

```text
init.c2VjcmV0LnR4dHwx.totallylegit.com
```

2. **Decodificar el índice**: `c2VjcmV0LnR4dHwx` en base64url es `secret.txt|1` → nombre del fichero y número de parte.

3. **Recoger las partes**: los demás TXT llevan el contenido troceado; se ordenan por el índice y se concatenan.

4. **Clave**: los `POST` dan el material auxiliar. `TryHarder` es la clave de RC4; el base64 del `/lootz` es sólo una pista.

```bash
# CyberChef: From Base64 (url safe) -> RC4 (key: TryHarder) -> Unzip
```

5. **Abrir** el ZIP resultante: `secret.txt` contiene la flag.

## Tropiezos

- **base64 vs base64url**: el alfabeto cambia (`-` y `_`); con base64 normal la decodificación falla.
- **Orden de las partes**: sin usar el índice del subdominio el ZIP sale corrupto.
- **Ruido**: aquí no hay; si el PCAP fuese mayor, filtrar por `dns.qry.type == 16` (TXT).

## Lecciones

- DNS es un canal de exfiltración habitual porque casi nunca se bloquea.
- Un prefijo con nombre de fichero y número de parte delata la reconstrucción.
- RC4 con clave débil no protege nada: es ofuscación.
