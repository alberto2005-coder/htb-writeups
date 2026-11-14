---
topic: OSINT reconnaissance
tags: [osint, reconnaissance, whois, certificates, github, shodan]
---

# OSINT reconnaissance

[🌐 English](reconnaissance.en.md) | **Español**

## Concepto

OSINT recopila información pública sobre una organización, sus dominios, empleados, tecnologías y exposiciones. El objetivo es construir un inventario verificable sin interactuar de forma intrusiva con el objetivo.

## Cuándo aplica

- Dominios y subdominios de una organización.
- Repositorios y filtraciones públicas.
- Metadatos de documentos e imágenes.
- Servicios expuestos indexados por buscadores.

## Procedimiento

1. Delimitar el alcance y las reglas de compromiso.
2. Enumerar dominios, certificados y DNS.
3. Revisar GitHub, filtraciones y metadatos.
4. Buscar tecnologías y servicios expuestos.
5. Validar y priorizar los hallazgos.

```bash
whois <DOMAIN>
curl -s 'https://crt.sh/?q=%25.<DOMAIN>&output=json' | jq -r '.[].name_value' | sort -u
theHarvester -d <DOMAIN> -b crtsh,bing
```

## Variantes

- Certificate transparency para subdominios.
- GitHub dorking y búsqueda de secretos.
- Shodan/Censys para servicios expuestos.
- Metadatos EXIF y documentos ofimáticos.

## Limitaciones

- La información puede estar desactualizada.
- Los resultados pueden incluir dominios ajenos.
- No todo hallazgo público es explotable.
- El alcance legal debe estar autorizado.

## Mitigación y detección

- Minimizar la exposición pública de servicios.
- Retirar secretos de repositorios y metadatos.
- Monitorizar certificados y dominios similares.
- Revisar periódicamente la huella digital.

## Referencias

- <https://attack.mitre.org/techniques/T1593/>
- <https://crt.sh/>
- <https://osintframework.com/>
