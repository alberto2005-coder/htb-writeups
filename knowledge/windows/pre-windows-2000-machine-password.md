---
topic: Contraseñas de equipos Pre-Windows 2000
tags: [windows, ad, machine-account, legacy, credentials]
---

# Contraseñas de equipos Pre-Windows 2000

[🌐 English](pre-windows-2000-machine-password.en.md) | **Español**

## Concepto

Las cuentas de equipo creadas con el flujo Pre-Windows 2000 pueden conservar una contraseña derivada del nombre del equipo en minúsculas, sin el `$`. Si además el grupo Pre-Windows 2000 Compatible Access tiene permisos de lectura sobre objetos, esa cuenta puede leer secretos como una GMSA.

## Cuándo aplica

- Existe una cuenta `NOMBRE$` creada con el método antiguo.
- El nombre del equipo es conocido y la contraseña no se rotó.
- La cuenta pertenece a Pre-Windows 2000 Compatible Access.

## Procedimiento

1. Enumerar cuentas de equipo y su grupo.
2. Probar el nombre en minúsculas como contraseña.
3. Leer los objetos permitidos, por ejemplo una GMSA.
4. Usar el secreto para moverte a otro sistema.

```bash
nxc smb <DC> -u 'FS01$' -p 'fs01' --shares
certipy-ad account read -u 'FS01$' -p 'fs01' -dc-ip <DC> -target <DC>
```

## Variantes

- Usar Kerberos en lugar de NTLM.
- Combinar con RBCD si la cuenta puede escribir en el DC.
- Leer `msDS-AllowedToActOnBehalfOfOtherIdentity`.

## Limitaciones

- La contraseña debe seguir siendo la original.
- La cuenta debe estar habilitada.
- Los permisos del grupo deben alcanzar el objeto objetivo.

## Mitigación y detección

- Rotar contraseñas de cuentas de equipo y eliminar el flujo legacy.
- Quitar cuentas innecesarias de Pre-Windows 2000 Compatible Access.
- Auditar lecturas de GMSA y objetos sensibles.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts>
- <https://attack.mitre.org/techniques/T1078/002/>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-assessment-unsecured-account-configuration>
