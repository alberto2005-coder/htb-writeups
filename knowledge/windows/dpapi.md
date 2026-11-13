---
topic: DPAPI
tags: [windows, dpapi, credentials, master-key, mimikatz, forensics]
---

# DPAPI

[🌐 English](dpapi.en.md) | **Español**

## Concepto

Data Protection API cifra secretos con claves derivadas del perfil de usuario o del equipo. Los blobs DPAPI se descifran con una master key, que a su vez depende de la contraseña del usuario o de la clave de recuperación del dominio. Es habitual en credenciales de navegadores, Zoom y aplicaciones corporativas.

## Cuándo aplica

- Credenciales guardadas por aplicaciones.
- Perfil de usuario comprometido.
- Acceso a master keys y blobs.
- Recuperación con clave de dominio o `NTDS.dit`.

## Procedimiento

1. Localizar blobs y master keys en el perfil.
2. Identificar el ámbito usuario o máquina.
3. Obtener la contraseña o el hash del usuario.
4. Descifrar la master key.
5. Usar la clave para descifrar los blobs.

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Protect" -Recurse -Force
mimikatz.exe "dpapi::masterkey /in:<MASTERKEY> /sid:<SID> /password:<PASSWORD>" "dpapi::cred /in:<BLOB>"
```

## Variantes

- DPAPI de usuario con contraseña.
- DPAPI de máquina con credenciales de sistema.
- Dominio con clave de recuperación o `NTDS.dit`.
- Blobs de navegador, Zoom, RDP o tareas programadas.

## Limitaciones

- Sin la contraseña o la master key no se descifra.
- La rotación de contraseña cambia las claves.
- El perfil debe estar completo.
- Algunos blobs requieren el contexto de la aplicación.

## Mitigación y detección

- Proteger perfiles y master keys.
- Usar credenciales de corta duración y MFA.
- Auditar acceso a `Protect` y a blobs.
- Alertar de lectura masiva de DPAPI y uso de Mimikatz.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptprotectdata>
- <https://github.com/gentilkiwi/mimikatz/wiki/howto-~-decrypt-credentials-file>
- <https://attack.mitre.org/techniques/T1555/003/>
