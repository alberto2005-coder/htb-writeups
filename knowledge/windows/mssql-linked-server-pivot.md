---
topic: Pivote con linked servers de MSSQL
tags: [windows, mssql, linked-server, xp_cmdshell, pivot]
---

# Pivote con linked servers de MSSQL

[🌐 English](mssql-linked-server-pivot.en.md) | **Español**

## Concepto

Un servidor MSSQL puede tener linked servers hacia otros hosts. Si el mapeo de login remoto es `sysadmin`, una cuenta de bajo privilegio en el primer servidor puede ejecutar consultas y comandos en el segundo.

## Cuándo aplica

- Se tiene acceso a MSSQL con un usuario válido.
- `enum_links` muestra un linked server.
- El mapeo remoto tiene privilegios altos.

## Procedimiento

1. Enumerar linked servers y mapeos.
2. Probar `SELECT SYSTEM_USER` en el servidor remoto.
3. Activar `xp_cmdshell` si es necesario.
4. Ejecutar comandos y obtener una shell.

```sql
enum_links
EXEC ('SELECT SYSTEM_USER') AT [DC02.darkzero.ext]
use_link [DC02.darkzero.ext]
enable_xp_cmdshell
xp_cmdshell whoami
```

## Variantes

- Usar `OPENQUERY` para consultas remotas.
- Aprovechar `sp_configure` para habilitar comandos.
- Saltar a un tercer servidor encadenado.

## Limitaciones

- El linked server debe estar configurado.
- El login remoto debe tener permisos.
- `xp_cmdshell` puede estar deshabilitado.

## Mitigación y detección

- Eliminar linked servers innecesarios.
- Evitar mapeos `sysadmin` y usar cuentas de mínimo privilegio.
- Deshabilitar `xp_cmdshell` y auditarlo.

## Referencias

- <https://learn.microsoft.com/en-us/sql/relational-databases/linked-servers/linked-servers-database-engine>
- <https://github.com/fortra/impacket>
- <https://attack.mitre.org/techniques/T1210/>
