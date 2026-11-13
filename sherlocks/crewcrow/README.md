---
sherlock: CrewCrow
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, zoom, dpapi, ntlm, credential-access]
---

# CrewCrow — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una reunión de Zoom sirve de pretexto para una intrusión. Se investigan los artefactos de la aplicación, credenciales protegidas con DPAPI y una base de datos de reuniones cifrada.

## Evidencias

- Perfil de usuario de Windows.
- Directorios de Zoom en `AppData`.
- Blobs DPAPI y hives del usuario.
- Base de datos de Zoom y logs de reuniones.
- Exportación de eventos y logs de autenticación.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigación

### 1. Artefactos de Zoom

Se localizan configuraciones, cachés, historial de reuniones y archivos de registro. Las rutas y versiones permiten identificar la cuenta y el equipo.

```powershell
Get-ChildItem "$env:APPDATA\Zoom" -Recurse -Force
```

### 2. DPAPI

Los secretos de usuario están protegidos con la clave maestra de DPAPI. Con el perfil y la contraseña o el hash del usuario se descifran los blobs; sin ellos, se documenta qué secreto queda fuera de alcance.

```powershell
dpapi::masterkey /in:<MASTERKEY> /sid:<SID> /password:<PASSWORD>
```

### 3. Base de datos y credenciales

La base de Zoom puede estar cifrada y contener IDs y contraseñas de reuniones. Se revisan también hashes NTLM y su crackeo offline. La línea temporal cruza acceso al perfil, descifrado y conexión a la reunión.

## Conclusiones

- Cuenta y equipo que participaron.
- Secretos recuperados y método.
- Reunión, identificador y participantes.
- IOCs: rutas, cuentas y hashes, redactados.

## Lecciones

- Las aplicaciones de videoconferencia guardan más metadatos de los visibles.
- DPAPI depende del contexto del usuario; sin perfil no se descifra.
- Una base cifrada puede ser inútil sin la clave, pero sus metadatos siguen siendo evidencia.

## Referencias

- <https://www.hackthebox.com/sherlocks/CrewCrow>
- <https://attack.mitre.org/techniques/T1555/003/>
- <https://learn.microsoft.com/en-us/windows/win32/seccng/cng-dpapi>
- <https://www.zoom.com/en/trust/security/>
