---
topic: MSSQL — pivote, ejecución y LAPS
tags: [windows, mssql, pivot, active-directory, laps]
---

# MSSQL — pivote, ejecución y LAPS

[🌐 English](mssql-pivot-laps.en.md) | **Español**

## Concepto

MSSQL con credenciales de usuario permite ejecutar consultas, leer archivos y, con `xp_cmdshell` o `EXECUTE AS`, ejecutar comandos. También sirve de pivote hacia otros hosts. En Active Directory, permisos para leer LAPS exponen la contraseña local del administrador, que se reutiliza para movimiento lateral y DCSync.

## Cuándo aplica

- MSSQL está expuesto y se tienen credenciales.
- El usuario tiene permisos de ejecución o `sysadmin`.
- BloodHound muestra derechos sobre objetos con LAPS.

## Procedimiento

1. Conectar con `mssqlclient.py` y enumerar privilegios.
2. Ejecutar comandos o consultas para moverse al siguiente host.
3. Enumerar AD y localizar permisos de lectura de LAPS.
4. Recuperar la contraseña y usarla para DCSync.

## Comandos

```bash
mssqlclient.py <USER>@<HOST> -windows-auth
SQL> enable_xp_cmdshell
SQL> xp_cmdshell whoami
bloodhound-python -u <USER> -p "<PASS>" -d <DOMAIN> -c All
# Lectura de LAPS
Get-ADComputer -Filter * -Properties ms-Mcs-AdmPwd | select Name,ms-Mcs-AdmPwd
```

## Variantes

- Usar `EXECUTE AS LOGIN` para cambiar de contexto.
- Leer archivos con `OPENROWSET`.
- Usar `certipy` o `secretsdump` tras obtener la contraseña LAPS.

## Limitaciones

- El usuario puede no tener `sysadmin`.
- LAPS puede estar migrado a Windows LAPS y usar otro atributo.
- El firewall puede limitar el pivote.

## Mitigación

- Aplicar mínimo privilegio en MSSQL y deshabilitar `xp_cmdshell`.
- Auditar quién puede leer LAPS.
- Segmentar la red y rotar contraseñas locales.

## Detección

- Consultas a `ms-Mcs-AdmPwd`.
- `xp_cmdshell` y procesos hijos de SQL Server.
- Autenticaciones laterales con cuentas de equipo.

## Referencias

- [0xdf — PivotAPI](https://0xdf.gitlab.io/2021/11/06/htb-pivotapi.html)
- [Microsoft — LAPS](https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
