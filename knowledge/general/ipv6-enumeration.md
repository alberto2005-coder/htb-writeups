---
topic: Enumeración IPv6
tags: [general, ipv6, snmp, enumeration, ssh]
---

# Enumeración IPv6

[🌐 English](ipv6-enumeration.en.md) | **Español**

## Concepto

Un host puede exponer servicios solo en IPv6. SNMP, DNS o el propio tráfico pueden revelar direcciones `dead:beef::/64` o enlaces locales. La enumeración IPv4 incompleta deja fuera SSH, HTTP o paneles internos.

## Cuándo aplica

- `nmap` solo muestra 80 en IPv4.
- SNMP responde con la tabla de interfaces.
- El host tiene un prefijo IPv6 documentado o predecible.

## Procedimiento

1. Enumerar SNMP y la tabla de direcciones.
2. Extraer el prefijo y el sufijo.
3. Escanear IPv6 con `nmap -6`.
4. Probar SSH/HTTP sobre la dirección encontrada.

```bash
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1.4.34
nmap -6 -p22,80 dead:beef::<SUFFIX>
ssh -6 user@dead:beef::<SUFFIX>
```

## Variantes

- Multicast DNS (`ff02::fb`).
- Router advertisements para descubrir prefijos.
- DNS AAAA para vhosts.
- Túneles 6to4 o Teredo.

## Limitaciones

- La dirección puede cambiar o requerir una interfaz concreta.
- El firewall puede filtrar ICMPv6 y romper la conectividad.
- No todos los clientes soportan `-6` o `ssh -6`.

## Mitigación y detección

- Inventariar direcciones IPv6 y servicios.
- Filtrar SNMP y limitar la exposición a la red interna.
- Aplicar las mismas reglas de firewall que en IPv4.
- Alertar de escaneos y accesos SSH sobre IPv6 no inventariado.

## Referencias

- <https://www.rfc-editor.org/rfc/rfc4291>
- <https://nmap.org/book/scan-methods-ipv6.html>
- <https://attack.mitre.org/techniques/T1046/>
