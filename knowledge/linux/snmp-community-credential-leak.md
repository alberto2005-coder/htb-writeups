---
topic: SNMP y fuga de credenciales
tags: [linux, snmp, credentials, enumeration]
---

# SNMP y fuga de credenciales

[🌐 English](snmp-community-credential-leak.en.md) | **Español**

## Concepto

SNMP puede exponer mucho más que métricas: nombres de host, procesos, scripts y cadenas de comunidad adicionales. Una comunidad de lectura con más permisos puede revelar credenciales de APIs o servicios.

## Cuándo aplica

- `161/udp` responde.
- La comunidad `public` devuelve información.
- Hay una comunidad adicional como `internal`.

## Procedimiento

1. Enumerar con `snmpwalk` y `public`.
2. Probar comunidades comunes con `snmpbrute.py`.
3. Recorrer los OIDs con la comunidad encontrada.
4. Buscar cadenas, scripts y credenciales.

```bash
snmpwalk -v2c -c public <IP>
python3 snmpbrute.py -t <IP>
snmpwalk -v2c -c internal <IP>
```

## Variantes

- Usar SNMPv3 con un usuario bootstrap.
- Leer `snmpd.conf` si se obtiene acceso local.
- Combinar con credenciales de API.

## Limitaciones

- SNMP debe estar expuesto.
- La comunidad debe tener permisos.
- La red puede filtrar UDP/161.

## Mitigación y detección

- Usar SNMPv3 y comunidades fuertes.
- Restringir SNMP a la red de gestión.
- No guardar credenciales en scripts accesibles por SNMP.

## Referencias

- <https://www.net-snmp.org/docs/man/snmpd.conf.html>
- <https://owasp.org/www-community/attacks/SNMP_Injection>
- <https://attack.mitre.org/techniques/T1046/>
