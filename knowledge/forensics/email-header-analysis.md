---
topic: Email header analysis
tags: [forensics, email, spf, dkim, dmarc, phishing, eml]
---

# Email header analysis

[🌐 English](email-header-analysis.en.md) | **Español**

## Concepto

Las cabeceras de un correo reconstruyen la cadena de entrega, el remitente real y el resultado de autenticación. SPF, DKIM y DMARC permiten comprobar si el mensaje fue autorizado por el dominio, aunque un fallo aislado no demuestra phishing por sí solo.

## Cuándo aplica

- Correo sospechoso con adjunto o enlace.
- Suplantación de un dominio conocido.
- Análisis de una campaña de phishing.
- Extracción de indicadores para bloqueo.

## Procedimiento

1. Leer las cabeceras `Received` de abajo arriba.
2. Comparar `From`, `Return-Path`, `Reply-To` y `Message-ID`.
3. Revisar `Authentication-Results` para SPF, DKIM y DMARC.
4. Decodificar adjuntos base64 y archivos anidados.
5. Calcular hashes y extraer dominios, IPs y URLs.

```bash
grep -iE '^(Received|From|Return-Path|Reply-To|Message-ID|Authentication-Results):' message.eml
grep -iE 'spf=|dkim=|dmarc=' message.eml
sha256sum message.eml
```

## Variantes

- SPF con `softfail` o múltiples saltos.
- DKIM con selector ausente o firma rota.
- DMARC en modo `p=none`.
- Adjunto ZIP con otro archivo comprimido dentro.

## Limitaciones

- Las cabeceras pueden ser falsificadas.
- Un SPF pass no garantiza legitimidad.
- Los reenviadores alteran la cadena.
- El contenido base64 puede estar ofuscado o cifrado.

## Mitigación y detección

- Aplicar SPF, DKIM y DMARC con política de rechazo.
- Bloquear adjuntos y macros no esperados.
- Alertar de discrepancias entre `From` y `Return-Path`.
- Correlacionar dominios, IPs y hashes con inteligencia.

## Referencias

- <https://datatracker.ietf.org/doc/html/rfc5321>
- <https://datatracker.ietf.org/doc/html/rfc7208>
- <https://attack.mitre.org/techniques/T1566/001/>
