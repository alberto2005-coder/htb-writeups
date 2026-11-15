---
topic: MSSQL — reutilización de contraseñas y RBCD
tags: [windows, mssql, password-spray, rbcd, activedirectory]
---

# MSSQL — reutilización de contraseñas y RBCD

[🇬🇧 English](mssql-password-reuse.en.md) | **Español**

## Concepto

MSSQL suele compartir credenciales con cuentas de dominio y locales. Un SQLi o un acceso a la base entrega un usuario de servicio; desde ahí `xp_cmdshell` da ejecución, un spray descubre cuentas con la misma contraseña y una de ellas puede tener derechos para configurar RBCD.

## Cuándo aplica

- Hay credenciales MSSQL o un SQLi en una aplicación.
- `xp_cmdshell` está disponible o se puede habilitar.
- La contraseña se reutiliza en cuentas de AD.

## Procedimiento

1. Autenticarse en MSSQL y enumerar usuarios y permisos.
2. Habilitar `xp_cmdshell` y obtener una shell.
3. Extraer credenciales de configuración y hacer spray.
4. Buscar derechos de escritura sobre equipos y configurar RBCD.

```bash
impacket-mssqlclient <DOMAIN>/<USER>:'<PASSWORD>'@<IP> -windows-auth
EXEC sp_configure 'show advanced options',1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;
```

```bash
netexec smb <DC> -u users.txt -p passwords.txt -d <DOMAIN>
```

## Variantes

- `xp_dirtree` para leer backups sin `xp_cmdshell`.
- `RunasCs` para usar credenciales locales.
- `SeImpersonate` para un potato si no hay RBCD.

## Limitaciones

- `xp_cmdshell` puede estar deshabilitado y sin permisos para cambiarlo.
- El spray bloquea cuentas si hay política de lockout.
- RBCD requiere un equipo controlado y derechos de escritura.

## Mitigación

- Contraseñas únicas y LAPS; evitar reutilización en servicios.
- Restringir `xp_cmdshell` y los permisos de la base.
- Auditar `msDS-AllowedToActOnBehalfOfOtherIdentity`.

## Detección

- `xp_cmdshell` y procesos hijos de SQL Server.
- Intentos de autenticación distribuidos con la misma contraseña.
- Escrituras de RBCD sobre objetos de equipo.

## Referencias

- [0xdf — Freelancer](https://0xdf.gitlab.io/2024/10/05/htb-freelancer.html)
- [Microsoft — xp_cmdshell](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/xp-cmdshell-transact-sql)
- [MITRE ATT&CK — T1110](https://attack.mitre.org/techniques/T1110/)
