---
challenge: Keep Tryin'
category: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, dns-exfil, base64url, rc4]
type: Forensics
---

# Keep Tryin' — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un PCAP de **26 paquetes** con tres cosas: un `POST /flag` con la palabra `TryHarder`, un `POST /lootz` con base64 («Keep trying, buffy») y **consultas DNS TXT con subdominios en base64url**. El nombre del primer subdominio decodifica a `secret.txt|1`: es una exfiltración por DNS. Los trozos se concatenan, se descifran con **RC4** usando `TryHarder` como clave y sale un ZIP con `secret.txt`.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Un PCAP de **26 paquetes** con tres cosas: un `POST /flag` con la palabra `TryHarder`, un `POST /lootz` con base64 («Keep trying, buffy») y **consultas DNS TXT con subdominios en base64url**. El nombre del primer subdominio decodifica a `secret.txt|1`: es una exfiltración por DNS. Los trozos se concatenan, se descifran con **RC4** usando `TryHarder` como clave y sale un ZIP con `secret.txt`.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `keeptryin.pcap` dentro de un ZIP.

## Lecciones aprendidas

- **base64 vs base64url**: el alfabeto cambia (`-` y `_`); con base64 normal la decodificación falla.
- **Orden de las partes**: sin usar el índice del subdominio el ZIP sale corrupto.
- **Ruido**: aquí no hay; si el PCAP fuese mayor, filtrar por `dns.qry.type == 16` (TXT).

- DNS es un canal de exfiltración habitual porque casi nunca se bloquea.
- Un prefijo con nombre de fichero y número de parte delata la reconstrucción.
- RC4 con clave débil no protege nada: es ofuscación.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [pcap-triage](../../knowledge/forensics/pcap-triage.md)
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
