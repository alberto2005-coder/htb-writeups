---
topic: Extracción de credenciales de Azure AD Connect
tags: [windows, active-directory, azure-ad-connect, adsync, credential-dump]
---

# Extracción de credenciales de Azure AD Connect

[🇬🇧 English](azure-ad-connect-dump.en.md) | **Español**

## Concepto

Azure AD Connect sincroniza identidades entre AD local y Microsoft Entra ID. Su base de datos local `ADSync` guarda las credenciales de la cuenta de servicio `MSOL_*` y del conector, cifradas de forma reversible. Con acceso administrativo al servidor y las claves del servicio, se pueden descifrar y reutilizar para DCSync o acceso a Entra ID.

## Cuándo aplica

- El DC o un servidor miembro ejecuta Azure AD Connect.
- El atacante tiene acceso local/administrativo o puede leer `ADSync.mdf`.
- La cuenta `MSOL_*` tiene privilegios de replicación o admin.

## Requisitos

1. Acceso al servidor con Azure AD Connect.
2. Capacidad de leer la base de datos `ADSync` y las claves de cifrado.
3. Herramienta de descifrado (`AdDecrypt`, `azuread_decrypt_msol.ps1`, Mimikatz).
4. Credenciales de una cuenta con permisos suficientes.

## Procedimiento

Se localiza la instalación y la base de datos:

```powershell
Get-ChildItem 'C:\Program Files\Microsoft Azure AD Sync\Data'
```

Se identifica la cuenta `MSOL_*` y el servicio:

```powershell
Get-Service ADSync
```

Con una herramienta de descifrado se extraen las credenciales:

```powershell
.\AdDecrypt.exe -Server <DC> -User <MSOL_USER> -Password '<MSOL_PASS>'
```

También se puede usar Mimikatz (`lsadump::dcsync`) si la cuenta `MSOL_*` tiene derechos de replicación.

## Variantes

- **AdDecrypt**: descifra la configuración local.
- **azuread_decrypt_msol.ps1**: script PowerShell.
- **Mimikatz DCSync**: usa la cuenta `MSOL_*` para replicar.
- **ADSync.mdf**: copia y análisis offline.

## Limitaciones

- Requiere acceso al servidor o a la base de datos.
- Las claves pueden rotar o estar protegidas por DPAPI.
- La cuenta `MSOL_*` puede no tener DCSync.
- Microsoft recomienda cuentas de servicio gestionadas.

## Mitigación

- Restringir acceso administrativo al servidor AAD Connect.
- Usar gMSA o cuentas gestionadas para el servicio.
- Auditar `MSOL_*` y sus permisos.
- Rotar credenciales y proteger `ADSync`.

## Detección

- Acceso a `ADSync.mdf` y a la carpeta `Data`.
- Ejecución de `AdDecrypt` o scripts de descifrado.
- DCSync desde la cuenta `MSOL_*`.
- Inicios de sesión de `MSOL_*` fuera del servidor de sincronización.

MITRE ATT&CK: T1003.006 (DCSync), T1555 (Credentials from Password Stores).

## Referencias

- <https://learn.microsoft.com/en-us/azure/active-directory/hybrid/>
- <https://attack.mitre.org/techniques/T1003/006/>
- <https://github.com/dirkjanm/adconnectdump>
