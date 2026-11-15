---
topic: API — lógica de invitación y command injection
tags: [web, api, invite, command-injection, authorization]
---

# API — lógica de invitación y command injection

[🇬🇧 English](api-invite-command-injection.en.md) | **Español**

## Concepto

Una API que reproduce un flujo de invitación suele exponer endpoints de generación y verificación, además de rutas de administración. Si el registro permite fijar `is_admin` o el endpoint de VPN pasa el usuario a `system`, la lógica de negocio se convierte en escalada y RCE.

## Cuándo aplica

- Hay un flujo de invitación o registro por API.
- El cliente puede enviar campos de rol o configuración.
- Un endpoint de administración genera comandos o archivos.

## Procedimiento

1. Enumerar `/api` y sus versiones; revisar el JavaScript ofuscado.
2. Generar y verificar un código de invitación.
3. Registrarse y probar `PUT /admin/settings/update` con `is_admin`.
4. Inyectar en el parámetro que llega al comando.

```bash
curl -s -X POST 'http://<IP>/api/v1/invite/generate'
curl -s -X PUT 'http://<IP>/api/v1/admin/settings/update' -H "Cookie: PHPSESSID=<SESSION>" --data '{"is_admin":true}'
```

## Variantes

- `is_admin`, `role` o `permissions` aceptados en el registro.
- Inyección con `;`, `|`, `$()` o backticks.
- Descarga de la VPN como vector de escritura.

## Limitaciones

- El rol puede validarse en el servidor.
- El comando puede usar `escapeshellarg`.
- La cuenta puede requerir verificación por email.

## Mitigación

- No aceptar roles desde el cliente; asignarlos en servidor.
- Parametrizar comandos y evitar `system` con entrada.
- Auditar los endpoints de administración y el registro.

## Detección

- Registros con `is_admin` o roles elevados.
- Peticiones a `/admin` desde cuentas nuevas.
- Caracteres de shell en parámetros de API.

## Referencias

- [OWASP — API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [0xdf — TwoMillion](https://0xdf.gitlab.io/2023/06/07/htb-twomillion.html)
- [PortSwigger — command injection](https://portswigger.net/web-security/os-command-injection)
