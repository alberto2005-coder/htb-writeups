---
challenge: TimeKORP
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, command-injection, php, cyber-apocalypse-2024]
---

# TimeKORP — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Una web que muestra la hora según un **formato** que llega por parámetro. El servidor construye una **orden de shell** con ese valor sin sanear: basta añadir `;` para ejecutar lo que se quiera. El código fuente viene con el reto, así que la vulnerabilidad se ve a la primera.

## Evidencia

- Instancia web y (según la versión del reto) el código PHP de la aplicación.

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

## Tropiezos

- **Codificar la URL**: `;` y espacios deben ir codificados (`%3B`, `%20`) según el cliente.
- **Comillas**: si el valor se interpola entre comillas simples, hay que cerrarlas antes del `;`.
- **Salida vacía**: probar `id` o `whoami` antes de asumir que no hay inyección.

## Lecciones

- Interpolar entrada del usuario en una orden de shell es inyección de comandos, aunque "sólo" sea un formato de fecha.
- El código fuente en el reto elimina la fase de adivinación.
- `escapeshellarg` y listas de formatos permitidos son la defensa.
