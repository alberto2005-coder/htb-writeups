---
topic: runas saved credentials
tags: [windows, privilege-escalation, runas, credentials, dpapi]
---

# runas saved credentials

[🇬🇧 English](runas-saved-credentials.en.md) | **Español**

## Concepto

`runas /savecred` almacena credenciales en el perfil del usuario para reutilizarlas sin volver a escribir la contraseña. Si un administrador las guardó en una sesión accesible, un usuario de bajo privilegio puede ejecutar procesos como esa cuenta.

## Cuándo aplica

- Windows con `runas /savecred` usado previamente.
- Perfil de usuario accesible con credenciales almacenadas.
- Cuenta guardada con privilegios altos.

## Requisitos

1. Shell en el host como usuario de bajo privilegio.
2. Credenciales guardadas en el perfil actual o accesible.
3. `runas.exe` disponible.

## Procedimiento

```powershell
runas /user:<DOMAIN>\\<USER> /savecred "cmd.exe /c whoami"
```

Si la credencial está guardada, el comando se ejecuta sin prompt. Para una reverse shell:

```powershell
runas /savecred /user:Administrator "powershell -e <base64>"
```

Las credenciales se almacenan en el Credential Manager/DPAPI del perfil. Se pueden enumerar con:

```powershell
cmdkey /list
```

## Variantes

- **Credential Manager**: entradas `Domain:interactive`.
- **DPAPI**: blobs en `%APPDATA%\\Microsoft\\Credentials`.
- **Programas con privilegios**: binarios que llaman a `runas /savecred`.
- **Tareas programadas**: guardan credenciales para ejecución.

## Limitaciones

- Solo funciona si la credencial fue guardada y es válida.
- El usuario debe poder iniciar el proceso.
- UAC puede bloquear la elevación.
- EDR puede alertar de `runas` con `/savecred`.

## Mitigación

- Evitar `runas /savecred` en cuentas privilegiadas.
- Limpiar Credential Manager y DPAPI.
- Usar cuentas de servicio gestionadas.
- Restringir acceso al perfil y auditar `cmdkey`.

## Detección

- Ejecución de `runas.exe` con `/savecred`.
- `cmdkey /list` desde cuentas no administrativas.
- Procesos hijos de `runas` con privilegios altos.
- Acceso a blobs DPAPI inusuales.

MITRE ATT&CK: T1555 (Credentials from Password Stores), T1078 (Valid Accounts).

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/runas>
- <https://attack.mitre.org/techniques/T1555/>
- <https://attack.mitre.org/techniques/T1078/>
