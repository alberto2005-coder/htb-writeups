---
topic: Credential reuse
tags: [general, credentials, reuse, default-credentials, spraying, authentication]
---

# Credential reuse

[🌐 English](credential-reuse.en.md) | **Español**

## Concepto

La reutilización de contraseñas y las credenciales por defecto permiten pasar de un servicio a otro sin explotar una vulnerabilidad. Un hallazgo en una aplicación, una base de datos o un archivo de configuración puede abrir SSH, SMB, WinRM o un panel administrativo.

## Cuándo aplica

- Credenciales obtenidas de una aplicación o backup.
- Usuarios con la misma contraseña en varios sistemas.
- Servicios con cuentas `admin/admin` o `guest`.
- Paneles de administración expuestos.

## Procedimiento

1. Inventariar usuarios y credenciales encontradas.
2. Probar la reutilización en servicios accesibles.
3. Verificar políticas de bloqueo antes de probar varias cuentas.
4. Priorizar cuentas de servicio y administradores.
5. Documentar cada acceso y evitar bloqueos.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --continue-on-success
nxc winrm <HOST> -u <USER> -p '<PASSWORD>'
ssh <USER>@<HOST>
```

## Variantes

- Contraseñas por defecto de routers, ERP o paneles.
- Reutilización entre base de datos y sistema operativo.
- Password spraying con una sola contraseña por varias cuentas.
- Credenciales en variables de entorno o repositorios.

## Limitaciones

- Los bloqueos de cuenta pueden interrumpir la prueba.
- MFA puede impedir el acceso aunque la contraseña sea válida.
- La reutilización puede limitarse por segmentación.
- Un login correcto no siempre implica privilegios.

## Mitigación y detección

- Prohibir credenciales por defecto y forzar rotación.
- Usar contraseñas únicas y un gestor de secretos.
- Aplicar MFA y bloqueo progresivo.
- Alertar de intentos distribuidos y logins desde hosts nuevos.

## Referencias

- <https://attack.mitre.org/techniques/T1078/>
- <https://attack.mitre.org/techniques/T1110/003/>
- <https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password>
