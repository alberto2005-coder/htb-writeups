---
topic: Credenciales de Edge y DPAPI
tags: [windows, dpapi, edge, credentials, privesc]
---

# Credenciales de Edge y DPAPI

[🌐 English](edge-dpapi-credential-extraction.en.md) | **Español**

## Concepto

Edge cifra las contraseñas guardadas con DPAPI. En el contexto de un usuario se pueden descifrar con su clave maestra; con una cuenta administrativa o un volcado del perfil se recuperan credenciales que a menudo se reutilizan en el dominio.

## Cuándo aplica

- Se tiene ejecución como el usuario propietario del perfil.
- El directorio `User Data` de Edge está accesible.
- Existe una clave maestra DPAPI o se puede obtener del DC.

## Procedimiento

1. Localizar `Local State` y la carpeta `Login Data`.
2. Extraer la clave cifrada y descifrarla con la clave maestra.
3. Abrir la base SQLite y descifrar las contraseñas.
4. Probar las credenciales en SMB, WinRM o LDAP.

```bash
DonPAPI.py DOMAIN/user:'<PASSWORD>'@<IP>
# o con el perfil montado:
python3 dpapi.py masterkey -file <MASTERKEY> -sid <SID> -password '<PASSWORD>'
python3 dpapi.py credential -file <CREDENTIAL> -key <KEY>
```

## Variantes

- Usar `SharpDPAPI` o `Mimikatz` en el host.
- Descifrar blobs de Credential Manager.
- Combinar con una sesión de Edge abierta.

## Limitaciones

- Sin la clave maestra el blob no se descifra.
- La cuenta debe poder cargar el perfil.
- Las credenciales pueden estar ausentes.

## Mitigación y detección

- Deshabilitar el guardado de contraseñas en el navegador.
- Proteger las claves DPAPI y limitar el acceso a perfiles.
- Usar credenciales gestionadas y MFA.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/secdoc/dpapi>
- <https://github.com/login-securite/DonPAPI>
- <https://attack.mitre.org/techniques/T1555/003/>
