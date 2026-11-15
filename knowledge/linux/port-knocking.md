---
topic: Port knocking — secuencias y servicios ocultos
tags: [linux, port-knocking, knockd, firewall, discovery]
---

# Port knocking — secuencias y servicios ocultos

[🌐 English](port-knocking.en.md) | **Español**

## Concepto

`knockd` escucha una secuencia de puertos y, al recibirla en orden, añade una regla de firewall que abre un servicio. La secuencia puede filtrarse en documentación, scripts o tráfico. No es autenticación: solo oculta el puerto hasta que se conoce el orden.

## Cuándo aplica

- Un servicio esperado no responde y el firewall lo filtra.
- Hay pistas de una secuencia de puertos en código o notas.
- El host ejecuta `knockd` o un script equivalente.

## Procedimiento

1. Buscar la secuencia en código, historial o documentación.
2. Enviar los puertos en orden con `knock`.
3. Comprobar que el servicio aparece en el escaneo.
4. Conectarse antes de que la regla expire.

## Comandos

```bash
grep -R "knock\|sequence" /var/www /opt 2>/dev/null
knock <IP> 40809 50212 46969
nmap -Pn -sCV -p22 <IP>
ssh <USER>@<IP>
```

## Variantes

- Usar `nc -z` para enviar los puertos uno a uno.
- Automatizar la secuencia con un script.
- Combinar con un cambio de fuente IP.

## Limitaciones

- La secuencia debe ser exacta.
- La regla expira y hay que repetirla.
- El firewall puede bloquear al atacante.

## Mitigación

- No usar port knocking como control de acceso.
- Exigir autenticación fuerte en el servicio.
- Monitorizar escaneos secuenciales.

## Detección

- Conexiones a puertos cerrados en orden.
- Reglas de firewall temporales.
- `knockd` en hosts que no lo necesitan.

## Referencias

- [knockd — manual](https://manpages.debian.org/testing/knockd/knockd.8.en.html)
- [0xdf — Oz](https://0xdf.gitlab.io/2019/01/12/htb-oz.html)
- [CWE-656 — Reliance on Security Through Obscurity](https://cwe.mitre.org/data/definitions/656.html)
