---
title: daloRADIUS — descubrimiento por SNMP y credenciales por defecto
tags: [linux, snmp, daloradius, radius, default-credentials]
---

# daloRADIUS — descubrimiento por SNMP y credenciales por defecto

[🇬🇧 English](daloradius-default-creds.en.md) | **Español**

## Concepto

daloRADIUS es una interfaz web de gestión de FreeRADIUS. Muchas instalaciones conservan el usuario `administrator` y una contraseña por defecto, y el portal se descubre a través de cadenas SNMP o de un vhost. Dentro, la tabla de usuarios puede contener hashes reutilizables en SSH.

## Cuándo aplica

- `161/udp` responde con la comunidad `public`.
- `snmpwalk` menciona `daloradius`, `radius` o una ruta `/daloradius`.
- El portal está en un puerto interno o en un vhost.

## Procedimiento

1. Enumerar SNMP y extraer cadenas y procesos.
2. Localizar el portal y probar credenciales documentadas.
3. Revisar usuarios, atributos y hashes.
4. Crackear y probar la contraseña en SSH.

```bash
snmpwalk -v2c -c public <IP> | grep -i -E 'daloradius|radius|http'
curl -s http://<IP>/daloradius/login.php
```

## Variantes

- El portal puede escuchar solo en `127.0.0.1`; usar túnel SSH.
- Los hashes pueden ser MD5, SHA1 o NT; identificar con `hashid`.
- La base MySQL puede ser accesible con las credenciales del portal.

## Limitaciones

- La comunidad SNMP puede ser distinta de `public`.
- Las credenciales por defecto pueden haberse cambiado.
- El portal puede requerir HTTPS o un vhost concreto.

## Mitigación y detección

- Cambiar credenciales por defecto y usar MFA.
- Restringir SNMP y el acceso al portal a la red de gestión.
- Almacenar contraseñas con bcrypt/Argon2 y no reutilizarlas.
- Auditar inicios de sesión y consultas a la tabla de usuarios.

## Referencias

- <https://github.com/lirantal/daloradius>
- <https://www.daloradius.com/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html>
