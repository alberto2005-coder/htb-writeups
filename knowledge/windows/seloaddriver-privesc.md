---
topic: Escalada con SeLoadDriverPrivilege
tags: [windows, privesc, driver, seloaddriverprivilege, capcom, edr]
---

# Escalada con SeLoadDriverPrivilege

[🌐 English](seloaddriver-privesc.en.md) | **Español**

## Concepto

`SeLoadDriverPrivilege` permite cargar y descargar controladores. Un usuario con este privilegio puede cargar un driver firmado pero vulnerable y usarlo para ejecutar código en modo kernel, saltarse las protecciones del sistema y obtener `NT AUTHORITY\SYSTEM`.

## Cuándo aplica

- Cuentas de servicio con `SeLoadDriverPrivilege` habilitado.
- Grupos como `Print Operators` o `Server Operators` en configuraciones antiguas.
- Sistemas sin bloqueo de drivers vulnerables.
- Capacidad de escribir en el registro y en `%TEMP%`.

## Procedimiento

1. Comprobar privilegios con `whoami /priv`.
2. Verificar si el privilegio está habilitado o se puede habilitar.
3. Identificar un driver firmado y vulnerable disponible.
4. Registrar el driver como servicio y cargarlo.
5. Ejecutar la acción privilegiada y limpiar el servicio.

```powershell
whoami /priv
reg add HKLM\System\CurrentControlSet\Services\<NAME> /v ImagePath /t REG_EXPAND_SZ /d "\??\C:\<PATH>\<DRIVER>.sys" /f
```

## Variantes

- Driver legado como Capcom.sys para deshabilitar la protección.
- Driver de hardware virtual o de monitorización vulnerable.
- Carga desde una ruta de usuario con `ImagePath` controlado.
- Uso de un servicio existente para apuntar al driver.

## Limitaciones

- El privilegio debe estar presente y habilitable.
- Windows puede bloquear drivers vulnerables con HVCI o listas de bloqueo.
- El driver debe ser compatible con la versión y arquitectura.
- La carga genera eventos y puede requerir reboot.

## Mitigación y detección

- Retirar `SeLoadDriverPrivilege` a cuentas no administrativas.
- Aplicar listas de drivers vulnerables y HVCI.
- Auditar la creación de servicios y la carga de drivers.
- Alertar de `reg add` en `CurrentControlSet\Services` y de drivers desde `%TEMP%`.

## Referencias

- <https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/load-and-unload-device-drivers>
- <https://attack.mitre.org/techniques/T1068/>
- <https://github.com/kkent030315/evil-mhyprot-cli>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
