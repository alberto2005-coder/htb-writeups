---
challenge: Manager
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, idor, http, dynamic-analysis, password-manager]
---

# Manager — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un gestor de contraseñas Android confía en un identificador enviado por el cliente para decidir qué bóveda devolver. Al interceptar el tráfico y cambiar el `id`, se accede a la bóveda de otro usuario y a la flag.

## Enunciado y superficie

- Mobile, Medium, retirado.
- Se entrega un APK de un gestor de contraseñas.
- La app permite registro, login y consulta de entradas.

```bash
apktool d manager.apk -o manager
jadx -d jadx manager.apk
```

## Reconocimiento

- La app usa HTTP y una API con endpoints de usuario y bóveda.
- `jadx` muestra parámetros como `userId`, `vaultId` o `id`.
- No hay comprobación local de propiedad; el servidor decide con el valor recibido.

```bash
grep -RInE 'userId|vaultId|/api/|Retrofit|OkHttp' jadx/sources | head -n 40
```

## Análisis

El cliente envía el identificador de la bóveda en la petición. Si el servidor no compara ese identificador con la sesión autenticada, se produce un IDOR. La app no firma la petición ni usa un token ligado al recurso.

## Explotación

1. Registrar dos cuentas y crear una entrada en cada una.
2. Configurar un proxy e interceptar la consulta de la bóveda.
3. Sustituir el `id` propio por el de la otra cuenta.
4. Reenviar y leer la respuesta.

```bash
# Con Burp o mitmproxy, modificar el parámetro y reenviar
GET /api/vault?id=<OTHER_ID> HTTP/1.1
Host: <HOST>
Authorization: Bearer <TOKEN>
```

La respuesta contiene la entrada de la otra cuenta y la flag.

## Evidencia

- Petición original y modificada.
- Respuesta con datos de la otra cuenta, redactados.
- Pantalla de la bóveda, con la flag redactada.

## Lecciones aprendidas

- Un identificador opaco no sustituye una comprobación de autorización.
- La app puede ser solo una interfaz: la seguridad depende del servidor.
- El análisis dinámico revela parámetros que el código ofusca.

## Mitigaciones y detección

- Derivar el propietario del recurso del token de sesión, no del cliente.
- Comprobar autorización en cada consulta.
- Usar identificadores no predecibles y registros de acceso.
- Alertar de consultas a recursos de otro usuario.

## Referencias

- <https://www.hackthebox.com/challenges/Manager>
- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1213/>
