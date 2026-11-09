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

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una web que muestra la hora según un **formato** que llega por parámetro. El servidor construye una **orden de shell** con ese valor sin sanear: basta añadir `;` para ejecutar lo que se quiera. El código fuente viene con el reto, así que la vulnerabilidad se ve a la primera.

## Enunciado y superficie

- Categoría Web; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Una web que muestra la hora según un **formato** que llega por parámetro. El servidor construye una **orden de shell** con ese valor sin sanear: basta añadir `;` para ejecutar lo que se quiera. El código fuente viene con el reto, así que la vulnerabilidad se ve a la primera.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Instancia web y (según la versión del reto) el código PHP de la aplicación.

## Lecciones aprendidas

- **Codificar la URL**: `;` y espacios deben ir codificados (`%3B`, `%20`) según el cliente.
- **Comillas**: si el valor se interpola entre comillas simples, hay que cerrarlas antes del `;`.
- **Salida vacía**: probar `id` o `whoami` antes de asumir que no hay inyección.

- Interpolar entrada del usuario en una orden de shell es inyección de comandos, aunque "sólo" sea un formato de fecha.
- El código fuente en el reto elimina la fase de adivinación.
- `escapeshellarg` y listas de formatos permitidos son la defensa.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Método

1. **Ver el parámetro**: la URL del tipo `?format=%H:%M` devuelve la hora formateada.

2. **Leer el código** si está disponible: aparece algo como

```php
$format = $_GET['format'] ?? 'H:i:s';
return shell_exec("date +'$format'");
```

3. **Inyectar**: cerrar la comilla y encadenar.

```text
?format=';cat /flag;'
?format=';id;'
```

4. **Variantes** si hay filtro: `$(cat /flag)`, backticks o `%0a` para salto de línea.

5. **Alternativa**: si el contenedor expone el `Dockerfile`, revela la ruta real de la flag.
