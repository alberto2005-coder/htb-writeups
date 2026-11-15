---
topic: ManageEngine ServiceDesk Plus — XXE y LFI
tags: [windows, manageengine, servicedesk, xxe, lfi, privesc]
---

# ManageEngine ServiceDesk Plus — XXE y LFI

[🌐 English](manageengine-servicedesk-xxe.en.md) | **Español**

## Concepto

ServiceDesk Plus con cuentas por defecto o invitado expone APIs y archivos. CVE-2017-9362 permite XXE para leer archivos, y CVE-2017-11511 permite un LFI; ambos pueden filtrar credenciales y llegar a la base o a SYSTEM.

## Cuándo aplica

- Panel SDP en 8080 con cuenta invitado o por defecto.
- La versión es anterior a los parches de 2017.
- Hay WinRM/SMB para reutilizar credenciales.

## Procedimiento

1. Probar cuentas por defecto y invitado.
2. Enviar un XML con entidad externa a la API.
3. Leer archivos de configuración y credenciales.
4. Usar el LFI para descargar archivos del panel.

## Comandos

```bash
# XML con <!ENTITY xxe SYSTEM "file:///C:/temp/it_logins.txt">
python3 mesep_xxe.py <IP> "C:\temp\Password Audit\it_logins.txt"
```

## Variantes

- XXE por SOAP o API REST.
- LFI con rutas relativas a cuatro directorios.
- Trigger de PostgreSQL para SYSTEM.

## Limitaciones

- La cuenta invitado puede estar deshabilitada.
- El XXE puede requerir autenticación.
- Los archivos sensibles pueden usar EFS.

## Mitigación

- Deshabilitar cuentas invitado y cambiar defaults.
- Actualizar SDP y deshabilitar entidades externas.
- Restringir WinRM y proteger EFS.

## Detección

- XML con `SYSTEM` o `ENTITY`.
- Accesos a `it_logins.txt` o backups.
- Uso de cuentas de servicio desde IPs nuevas.

## Referencias

- [0xdf — Helpline](https://0xdf.gitlab.io/2019/08/17/htb-helpline.html)
- [NVD — CVE-2017-9362](https://nvd.nist.gov/vuln/detail/CVE-2017-9362)
- [NVD — CVE-2017-11511](https://nvd.nist.gov/vuln/detail/CVE-2017-11511)
