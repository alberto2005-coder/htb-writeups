---
topic: DNS enumeration
tags: [general, dns, enumeration, zone-transfer, subdomains, recon]
---

# DNS enumeration

[🌐 English](dns-enumeration.en.md) | **Español**

## Concepto

DNS revela nombres de hosts, servicios internos, correo y subdominios. La enumeración busca transferencias de zona mal configuradas, registros wildcard, subdominios olvidados y registros TXT con información sensible.

## Cuándo aplica

- Dominio con NS o MX expuestos.
- Servidor DNS autoritativo accesible.
- Aplicación con virtual hosts.
- Certificados de transparencia con subdominios.

## Procedimiento

1. Consultar NS, MX y TXT.
2. Intentar una transferencia de zona.
3. Enumerar subdominios y comparar respuestas.
4. Resolver hosts internos y rangos.
5. Cruzar con certificados y OSINT.

```bash
dig +short NS <DOMAIN>
dig +short MX <DOMAIN>
dig AXFR <DOMAIN> @<NAMESERVER>
dnsrecon -d <DOMAIN> -t std,brt
```

## Variantes

- Transferencia de zona completa.
- Wildcard DNS que oculta subdominios reales.
- Registros TXT con tokens de verificación.
- DNS interno accesible por VPN o pivote.

## Limitaciones

- La transferencia de zona suele estar deshabilitada.
- Los subdominios pueden no resolver públicamente.
- Los wildcard generan falsos positivos.
- El DNS puede estar segmentado.

## Mitigación y detección

- Restringir `AXFR` a servidores secundarios autorizados.
- Auditar registros y eliminar los obsoletos.
- Monitorizar consultas masivas y transferencias.
- Revisar certificados y registros TXT periódicamente.

## Referencias

- <https://www.rfc-editor.org/rfc/rfc1035>
- <https://attack.mitre.org/techniques/T1590/002/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-dns.html>
