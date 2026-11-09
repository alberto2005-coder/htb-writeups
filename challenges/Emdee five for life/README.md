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

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

- Cada `GET /` emite una cadena distinta y la guarda en la sesión (cookie `PHPSESSID`).
- El `POST /` compara el `hash` enviado con el MD5 de la cadena emitida para **esa** sesión.
- Enviar el hash de una cadena vieja, o reutilizar la sesión sin volver a leer la cadena, devuelve `Too slow!`.

Es un ejercicio de tiempo, no de criptografía: MD5 no se rompe, se calcula.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

```python
import re, hashlib, requests

s = requests.Session()
r = s.get("http://<IP>:<PORT>/")
cadena = re.search(r"<h3 align='center'>([A-Fa-f0-9]+)</h3>", r.text).group(1)
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

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Variantes y tropiezos

- **Regex demasiado laxa**: capturar el `<h3>` equivocado (hay varios) y hashear texto decorativo.
- **Sesión nueva en cada petición**: `requests.get` sin `Session` pierde la cookie y la cadena nunca coincide.
- **MD5 en mayúsculas**: el servidor compara en minúsculas; `hexdigest()` ya lo devuelve así.
