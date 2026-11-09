---
challenge: Easy Phish
type: OSINT
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [osint, phishing, dns, spf, dmarc]
---

# Easy Phish — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## Enunciado

Una empresa detecta correos que suplantan su dominio. Hay que localizar la infraestructura del atacante: dominio parecido, registros DNS y servidor de correo.

## Método

1. **Dominio señuelo**: comparar el legítimo con variantes (typosquatting, guion, TLD distinto). `dnstwist` genera y resuelve candidatos:

   ```bash
   dnstwist --registered <empresa>.com
   ```

2. **DNS**: `dig` sobre el sospechoso:

   ```bash
   dig +short A <dominio-sospechoso>
   dig +short MX <dominio-sospechoso>
   dig +short TXT <dominio-sospechoso>
   ```

   Un `TXT` con `v=spf1` y otro con `v=DMARC1` confirman que el atacante montó correo.

3. **Reputación y antigüedad**: `whois`, Certificate Transparency (`crt.sh`), VirusTotal y URLScan. Un dominio de días con certificado reciente es la señal.

4. **Cabeceras del correo**: `Received`, `Return-Path`, `Message-ID` y `Authentication-Results`. El `Return-Path` suele apuntar al dominio del atacante y el `Received` al servidor real.

5. **IP del servidor**: resolver el `A`/`MX` y buscar la IP en Shodan/Censys para ver el panel de correo.

## Hallazgos (patrón)

```text
A     <dominio> -> <IP>
MX    <dominio> -> mail.<dominio>
TXT   "v=spf1 a mx ip4:<IP> ~all"
TXT   "v=DMARC1; p=none;"
```

La combinación de SPF/DMARC propios y un MX dedicado indica infraestructura de phishing activa.

## Errores típicos

- **`dnstwist` sin resultados registrados** → el dominio aún no resuelve; mira `--registered` y CT.
- **El correo usa un dominio legítimo comprometido** → revisa `Received` en orden inverso, no solo el `From`.
- **Muchas IPs** → separa `A` de `MX`; el correo sale por el MX.
- **Sin SPF/DMARC** → el atacante usa un relay; sigue el `Return-Path`.

## Lecciones

- El `From` no prueba nada; `Return-Path` + `Received` sí.
- Certificate Transparency encuentra dominios antes de que estén indexados.
- Un SPF permisivo (`~all`) explica por qué el correo no se marcó como spam.

MITRE: T1583.001, T1566.002, T1596.
