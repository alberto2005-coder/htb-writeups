---
topic: AD Recycle Bin y objetos borrados
tags: [active-directory, windows, recycle-bin, deleted-objects, credentials, dfir]
---

# AD Recycle Bin: objetos borrados como fuente de credenciales

[🇬🇧 English](ad-recycle-bin.en.md) | **Español**

## Idea

Cuando se elimina un objeto en Active Directory no desaparece: pasa a un estado **tombstone** y sigue en el directorio con sus atributos durante un tiempo. Con la función opcional **Recycle Bin** habilitada, el objeto conserva *todos* sus atributos y se puede restaurar; sin ella, solo quedan unos pocos (el resto se borra al eliminar). En ambos casos, un atacante con permiso para leer objetos borrados puede recuperar contraseñas, descripciones y pertenencias a grupos que la organización cree eliminadas.

## Cuándo aplica

- El dominio tiene habilitada la función opcional `Recycle Bin Feature` y hay cuentas con el rol **AD Recycle Bin** (o `Domain Admin`).
- Se quiere persistencia silenciosa: recuperar una cuenta borrada y usarla en lugar de crear una nueva.
- Forense: reconstruir cuentas que existieron, cuándo se borraron y qué permisos tenían.
- Caso típico: una cuenta temporal de administración se borra en vez de deshabilitarse y su contraseña sigue siendo válida.

## Comandos

Comprobar si la función está habilitada:

```powershell
Get-ADOptionalFeature -Filter 'Name -eq "Recycle Bin Feature"' |
  Select-Object Name, EnabledScopes
```

Listar objetos borrados con todos sus atributos:

```powershell
Get-ADObject -filter 'isDeleted -eq $true' -includeDeletedObjects -property * |
  Select-Object Name, sAMAccountName, whenCreated, whenChanged, lastKnownParent
```

Buscar un atributo concreto (por ejemplo, uno heredado con contraseña):

```powershell
Get-ADObject -filter 'isDeleted -eq $true -includeDeletedObjects -property *' |
  Where-Object { $_.cascadeLegacyPwd } |
  Select-Object Name, cascadeLegacyPwd
```

Restaurar el objeto y leerlo ya como cuenta activa:

```powershell
Restore-ADObject -Identity '<GUID>'
Get-ADUser -Identity '<sAMAccountName>' -Properties *
```

Equivalente por LDAP, con el control `LDAP_SERVER_SHOW_DELETED_OID` (`1.2.840.113556.1.4.417`):

```bash
ldapsearch -x -H ldap://<IP> -D '<USER>@<DOMAIN>' -w '<PASSWORD>' \
  -b 'CN=Deleted Objects,DC=<DOMAIN>,DC=<TLD>' \
  -E '!1.2.840.113556.1.4.417=::/' \
  '(objectClass=*)' name sAMAccountName
```

## Variantes

- **Sin Recycle Bin habilitado**: los tombstones solo conservan `objectSid`, `sAMAccountName`, `lastKnownParent`, `whenCreated` y poco más. Se puede "reanimar" el objeto cambiando su `isDeleted`, pero se pierde casi todo el resto.
- **`msDS-deletedObjectLifetime`**: por defecto 180 días con Recycle Bin; al agotarse, el objeto se elimina de verdad. Si el valor es 0, no caduca nunca y el riesgo es permanente.
- **Cuentas de servicio borradas**: al restaurarlas recuperan sus SPN y sus permisos, no solo la contraseña.
- **Alternativa defensiva**: la papelera de AD es también la forma correcta de recuperar un borrado accidental, así que restringirla tiene coste operativo; se compensa con auditoría.

## Blindaje

- Deshabilitar y rotar la contraseña antes de eliminar cualquier cuenta, sobre todo las privilegiadas.
- Vaciar atributos sensibles (`description`, `info`, atributos personalizados) antes de borrar.
- Limitar el grupo **AD Recycle Bin** a cuentas administrativas nominales, con MFA y auditoría, nunca a cuentas de servicio.
- Reducir `msDS-deletedObjectLifetime` si la política lo permite y revisar los atributos personalizados que guardan secretos.

## Detección

- **4662** sobre objetos del directorio con acceso de lectura a `Deleted Objects`, y consultas LDAP con el control `1.2.840.113556.1.4.417`.
- **4688** (o Sysmon 1) con `Get-ADObject -includeDeletedObjects` o `Restore-ADObject` en la línea de comandos.
- Evento **4780**/auditoría de cambios en grupos privilegiados si alguien añade una cuenta a `AD Recycle Bin`.
- En el DC, las consultas anónimas o de cuentas de servicio fuera de horario al contenedor `CN=Deleted Objects`.

MITRE: T1087.002 (domain account discovery), T1078.002 (domain accounts), T1098 (account manipulation), T1552.001 (credentials in files).

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/1e3974d4-3c3d-4a49-9c9a-3f0e0e3fbe8a>
- <https://attack.mitre.org/techniques/T1098/>
- <https://www.hackthebox.com/machines/cascade>
