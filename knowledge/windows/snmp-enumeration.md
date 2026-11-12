---
topic: SNMP enumeration
tags: [windows, snmp, enumeration, credentials, network]
---

# SNMP enumeration

[🇬🇧 English](snmp-enumeration.en.md) | **Español**

## Concepto

SNMP expone información de gestión del sistema (interfaces, procesos, software, usuarios y a veces credenciales) si usa comunidades débiles o versiones sin autenticación. En Windows, el servicio puede revelar nombres de equipo, dominios, cuentas y cadenas de configuración.

## Cuándo aplica

- Puerto 161/UDP abierto.
- Comunidad `public`/`private` o SNMPv1/v2c.
- Dispositivos de red, impresoras o servidores Windows con SNMP habilitado.

## Requisitos

1. IP objetivo y conectividad UDP.
2. `snmpwalk`/`snmp-check`/`onesixtyone`.
3. Diccionario de comunidades.

## Procedimiento

```bash
onesixtyone -c communities.txt <IP>
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1
snmpwalk -v2c -c public <IP> 1.3.6.1.4.1
```

Se revisan OIDs de sistema, procesos, software instalado y usuarios. Las cadenas de configuración pueden incluir rutas, dominios y contraseñas.

```bash
snmp-check <IP> -c public
```

En Windows, el MIB `1.3.6.1.2.1.25` expone hardware y software; los OIDs de empresa pueden contener configuraciones propietarias.

## Variantes

- **SNMPv1/v2c**: comunidad en claro.
- **SNMPv3**: requiere usuario y autenticación; probar `noAuthNoPriv`.
- **Trap receiver**: escuchar traps para descubrir dispositivos.
- **Windows SNMP**: extensión de gestión con información de procesos.

## Limitaciones

- UDP puede estar filtrado.
- La comunidad puede ser no estándar.
- SNMPv3 con `authPriv` no se enumera sin credenciales.
- La información puede estar desactualizada.

## Mitigación

- Deshabilitar SNMP si no es necesario.
- Usar SNMPv3 con `authPriv`.
- Cambiar comunidades por defecto y aplicar ACLs.
- No almacenar secretos en OIDs.

## Detección

- Consultas `snmpwalk` desde hosts no autorizados.
- Picos de tráfico UDP/161.
- Intentos con comunidades comunes.
- Acceso a OIDs de configuración/credenciales.

MITRE ATT&CK: T1046 (Network Service Discovery), T1552 (Unsecured Credentials).

## Referencias

- <https://www.net-snmp.org/>
- <https://attack.mitre.org/techniques/T1046/>
- <https://book.hacktricks.xyz/network-services-pentesting/pentesting-snmp>
