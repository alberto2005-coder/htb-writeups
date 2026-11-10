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

## TL;DR

El reto no tiene infraestructura de atacante: la pregunta es **por qué** los correos falsos de `secure-startup.com` no se marcan como spam. La respuesta está en sus propios registros DNS: un **SPF** con `?all` (neutral, no `-all`) y un **DMARC** con `p=none`. Cada registro lleva además media flag.

## Enunciado y superficie

«Customers of secure-startup.com have been receiving some very convincing phishing emails, can you figure out why?» No hay binario ni web: solo un dominio y la pista de que algo falla en la autenticación de correo.

## Reconocimiento

```bash
dig +short TXT secure-startup.com
dig +short TXT _dmarc.secure-startup.com
dig +short MX secure-startup.com
```

```text
"v=spf1 a mx ?all - HTB{RIP_SPF_Always_2nd"
"v=DMARC1;p=none;_F1ddl3_2_DMARC}"
```

## Análisis

- **SPF**: `?all` significa *neutral*. Un receptor no puede afirmar que el emisor esté autorizado, pero tampoco lo rechaza; con `-all` (fail) el correo suplantado se habría marcado. El `a`/`mx` autoriza solo los hosts del propio dominio.
- **DMARC**: `p=none` pide informes pero **no da instrucción de rechazo** a quien recibe. Sin alineación obligatoria ni política `quarantine`/`reject`, el spoofing pasa.
- **DKIM**: no hay registro publicado, así que no hay segunda barrera que compensa.

La flag está partida entre los dos TXT: se concatenan en orden (SPF primero, DMARC después).

## Explotación

```bash
dig +short TXT secure-startup.com | tr -d '"'
dig +short TXT _dmarc.secure-startup.com | tr -d '"'
# unir las dos mitades dentro de HTB{...}
```

## Evidencia

- Salida de `dig` con el SPF y el DMARC (valores redactados en la ficha).
- Explicación de por qué `?all` y `p=none` permiten la suplantación.

## Lecciones aprendidas

- **`?all` no protege**: solo `-all` indica que ningún otro host puede enviar por el dominio.
- **`p=none` es modo observación**: sin `quarantine`/`reject`, DMARC no frena nada.
- SPF sin DKIM ni DMARC deja la puerta abierta: los tres se complementan.
- La flag en los TXT es un truco del reto; en la vida real el dato es la política, no el texto.

## Mitigaciones y detección

- Publicar `v=spf1 ... -all` con todos los emisores legítimos (incluidos los SaaS) y revisar el límite de 10 búsquedas DNS.
- DMARC en `p=quarantine` o `p=reject` con `rua`/`ruf` y alineación estricta.
- DKIM firmando todo el correo saliente.
- Detección: correos con `Authentication-Results` que muestren `spf=neutral` o `dmarc=none` para el propio dominio.

## Referencias

- [RFC 7208 (SPF)](https://www.rfc-editor.org/rfc/rfc7208)
- [RFC 7489 (DMARC)](https://www.rfc-editor.org/rfc/rfc7489)
- [phishing-infrastructure](../../knowledge/osint/phishing-infrastructure.md)
