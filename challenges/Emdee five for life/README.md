---
challenge: Emdee five for life
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, md5, scripting, automation, python]
---

# Emdee five for life — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

La página genera una cadena aleatoria y pide su **MD5**. Si se envía a mano se llega tarde: la cadena caduca y la respuesta cambia. El reto es de automatización: sesión HTTP, extraer la cadena con una regex, calcular el hash y publicar el resultado en menos de un segundo. Cuando el ciclo es lo bastante rápido, la respuesta trae la flag.

## Enunciado y superficie

```text
Encrypt this string into md5 and send it back.
String: 6Ml1m0JmWq
```

Un formulario con un único campo `hash`.

## Reconocimiento

El HTML tiene un `<h3 align='center'>` con la cadena y un formulario `POST` con un único campo `hash`. El servidor responde `Set-Cookie: PHPSESSID=...`; la cadena vive en esa sesión.

## Análisis del código

No hay código que auditar: es un ejercicio de estado. Cada `GET` emite cadena nueva y cada `POST` compara contra la de la sesión; sin cookie compartida, la comparación siempre falla.

## Explicación del fallo

- Cada `GET /` emite una cadena distinta y la guarda en la sesión (cookie `PHPSESSID`).
- El `POST /` compara el `hash` enviado con el MD5 de la cadena emitida para **esa** sesión.
- Enviar el hash de una cadena vieja, o reutilizar la sesión sin volver a leer la cadena, devuelve `Too slow!`.

Es un ejercicio de tiempo, no de criptografía: MD5 no se rompe, se calcula.

## Reproducción local

Se puede probar el bucle contra cualquier formulario equivalente; lo importante es reutilizar el objeto `Session` y no crear uno por petición.

## Explotación

```python
import re, hashlib, requests

s = requests.Session()
r = s.get("http://<IP>:<PORT>/")
cadena = re.search(r"<h3 align='center'>([A-Za-z0-9]+)</h3>", r.text).group(1)
# si el HTML cambia, anclar en la etiqueta que envuelva el texto aleatorio
digest = hashlib.md5(cadena.encode()).hexdigest()
r = s.post("http://<IP>:<PORT>/", data={"hash": digest})
print(r.text)
```

```text
HTB{<flag>}
```

Con Burp también se resuelve: `Ctrl+R` sobre la petición, `Send to Repeater`, y usar el pre-request script o el Intruder con un payload calculado. La vía limpia es el script.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un control "anti-bot" basado en tiempo se rompe con un cliente HTTP; no aporta seguridad, solo fricción.
- Automatizar el ciclo completo (leer, transformar, enviar manteniendo estado) es la habilidad que entrena el reto.
- Mitigación real: límites de tasa por cuenta, CAPTCHA y verificación de sesión, no un temporizador de un segundo.

## Mitigaciones y detección

El control «anti-bot» es un temporizador, y un cliente HTTP lo gana siempre.

- Si se quiere frenar automatización: límites por cuenta/IP, CAPTCHA y pruebas de trabajo, no un plazo de un segundo.
- Detección: ráfagas de `GET`/`POST` con la misma sesión y latencia mínima.

## Variantes y tropiezos

- **Regex demasiado laxa**: capturar el `<h3>` equivocado (hay varios) y hashear texto decorativo.
- **Sesión nueva en cada petición**: `requests.get` sin `Session` pierde la cookie y la cadena nunca coincide.
- **MD5 en mayúsculas**: el servidor compara en minúsculas; `hexdigest()` ya lo devuelve así.
