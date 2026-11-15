---
topic: SNMP e IPv6 — descubrimiento de servicios ocultos
tags: [linux, snmp, ipv6, discovery, command-injection]
---

# SNMP e IPv6 — descubrimiento de servicios ocultos

[🌐 English](snmp-ipv6-discovery.en.md) | **Español**

## Concepto

SNMP expone interfaces, procesos y tablas del sistema, incluidas direcciones IPv6. Un servicio puede escuchar solo en IPv6 y quedar fuera de un escaneo IPv4. `snmpwalk` revela la dirección y el puerto; el servicio suele tener la misma superficie vulnerable que su equivalente IPv4, pero menos filtrado.

## Cuándo aplica

- SNMP responde con comunidades por defecto.
- El escaneo IPv4 no muestra servicios esperados.
- La aplicación o el sistema tiene interfaces IPv6.

## Procedimiento

1. Enumerar SNMP y revisar interfaces y procesos.
2. Extraer direcciones IPv6 y puertos.
3. Acceder al servicio por IPv6 con `curl -g` o el cliente adecuado.
4. Explotar la vulnerabilidad del servicio.

## Comandos

```bash
snmpwalk -v2c -c public <IP>
snmpwalk -v2c -c public <IP> ipAddresses
snmpwalk -v2c -c public <IP> tcpConnTable
curl -g -6 "http://[<IPv6>]/index.php?cmd=id"
```

## Variantes

- Usar `snmp-check` para un resumen.
- Enumerar procesos con `hrSWRunTable`.
- Combinar con `nmap -6` si el host es alcanzable.

## Limitaciones

- La comunidad debe ser válida.
- IPv6 puede no ser alcanzable desde el atacante.
- El servicio puede estar filtrado por firewall.

## Mitigación

- Cambiar comunidades y restringir SNMP.
- Aplicar el mismo filtrado a IPv6 que a IPv4.
- Inventariar servicios que escuchan en todas las interfaces.

## Detección

- `snmpwalk` desde hosts no autorizados.
- Consultas a tablas de interfaces y procesos.
- Acceso a servicios IPv6 no inventariados.

## Referencias

- [0xdf — Mischief](https://0xdf.gitlab.io/2019/01/05/htb-mischief.html)
- [Net-SNMP — snmpwalk](http://www.net-snmp.org/docs/man/snmpwalk.html)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
