---
sherlock: TeamWork
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, osint, nft, infrastructure, typosquatting]
---

# TeamWork — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un grupo supuestamente benéfico promociona un proyecto NFT y pide a los usuarios conectar sus carteras. Se entrega un dominio, capturas y un archivo con mensajes; hay que atribuir la infraestructura y el modus operandi.

## Evidencias

- Dominio, certificados y registros DNS.
- Capturas del sitio y mensajes de redes sociales.
- Archivo ZIP con el sitio clonado.

```bash
whois <DOMAIN>
dig +short <DOMAIN> A
curl -sI https://<DOMAIN>/
```

## Investigación

### 1. Huella del sitio

Se comparan recursos, favicon y certificados con el proyecto legítimo. Los enlaces de donación y el flujo de conexión de cartera revelan el objetivo.

```bash
curl -s https://<DOMAIN>/ | grep -Eo 'https?://[^" ]+' | sort -u
```

### 2. Infraestructura

DNS, ASN y certificados relacionan dominios. Se buscan variantes tipográficas y cuentas con el mismo identificador. No se interactúa con carteras ni se envían fondos.

```bash
curl -s 'https://crt.sh/?q=%25.<DOMAIN>&output=json'
```

### 3. Narrativa y atribución

Los mensajes, nombres de archivo y metadatos del ZIP se comparan con campañas conocidas. La atribución se expresa con confianza y evidencia, no como certeza absoluta.

## Conclusiones

- El sitio imita una marca y desvía fondos.
- Los certificados y el ASN agrupan la infraestructura.
- La narrativa benéfica reduce la sospecha.
- La atribución es probable, no definitiva.

## Lecciones

- OSINT requiere no interactuar con el objetivo.
- Los certificados son una fuente de pivote.
- El archivo clonado conserva rutas y metadatos.
- La inteligencia se documenta con niveles de confianza.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://attack.mitre.org/techniques/T1583/001/>
- <https://attack.mitre.org/techniques/T1566/>
