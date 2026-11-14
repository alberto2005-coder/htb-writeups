---
topic: AlwaysInstallElevated
tags: [windows, privesc, msi, registry, gpo]
---

# AlwaysInstallElevated

[🌐 English](alwaysinstallelevated.en.md) | **Español**

## Concepto

La directiva `AlwaysInstallElevated` permite a cualquier usuario instalar paquetes MSI con privilegios de SYSTEM. Si las dos claves (HKLM y HKCU) valen `1`, un MSI malicioso se ejecuta elevado sin credenciales.

## Cuándo aplica

- Equipos de escritorio con instalación libre de software.
- GPO que habilita la directiva en usuario y equipo.
- Usuario estándar con capacidad de ejecutar `msiexec`.

## Procedimiento

1. Consultar ambas claves.
2. Generar un MSI que añada un administrador o una shell.
3. Instalar con `msiexec /quiet`.
4. Verificar el contexto.

```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
msfvenom -p windows/adduser USER=<USER> PASS=<PASSWORD> -f msi -o evil.msi
msiexec /quiet /qn /i evil.msi
```

## Variantes

- MSI con `CustomAction` para lanzar un binario.
- `InstallExecuteSequence` para ejecutar como SYSTEM.
- Combinación con `SeImpersonate` si la directiva no está activa.

## Limitaciones

- Solo funciona si ambas claves están a `1`.
- `msiexec` puede estar restringido por AppLocker/WDAC.
- El MSI debe ser aceptado por el instalador.

## Mitigación y detección

- Deshabilitar `AlwaysInstallElevated` en ambas ramas.
- Restringir instalaciones a administradores.
- Alertar de `msiexec` lanzado por usuarios estándar y de MSI desde rutas de usuario.
- Auditar cambios de GPO.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated>
- <https://gtfobins.github.io/gtfobins/msiexec/>
- <https://attack.mitre.org/techniques/T1548/002/>
