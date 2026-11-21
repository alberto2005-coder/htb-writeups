---
machine: Shoppy
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nosql, mongodb, mattermost, reversing, docker, privesc]
---

# Shoppy — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La tienda usa MongoDB y el login es vulnerable a inyección NoSQL: `admin'||'a'=='a` autentica como administrador sin conocer la contraseña. El panel permite exportar usuarios y el mismo truco devuelve el hash de `josh`, que se crackea. Esa cuenta abre Mattermost, donde hay credenciales de `jaeger` para SSH. `jaeger` puede ejecutar como `deploy` un gestor de contraseñas; el binario compara la entrada con una cadena de 16 bits que `strings -el` revela, y tras extraer la contraseña de `deploy` se entra en esa cuenta. `deploy` pertenece al grupo `docker`, así que un contenedor con el disco del host montado da acceso a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,9093 <IP>
```

- `22`: OpenSSH 8.4p1 Debian.
- `80`: nginx 1.23.1, tienda y Mattermost por virtual host.
- `9093`: servicio HTTP auxiliar.

```bash
echo '<IP> shoppy.htb mattermost.shoppy.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://shoppy.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

`/login` redirige a un formulario y `/admin` a `/login`. La respuesta tarda y devuelve un `504` con una comilla simple, lo que descarta SQLi clásica y apunta a una consulta NoSQL. Mattermost se publica en `mattermost.shoppy.htb` y muestra su propio formulario de acceso.

## Foothold

El login acepta una expresión booleana en el usuario:

```text
username=admin'||'a'=='a&password=<PASSWORD>
```

La consulta resultante se evalúa como verdadera para el usuario `admin` y devuelve una sesión. El panel tiene una búsqueda de usuarios que exporta un JSON; con una inyección similar se obtiene el registro de `josh` y su hash MD5. Tras crackearlo, las credenciales abren Mattermost.

```text
username=admin'||'1'=='1&password=<PASSWORD>
```

En Mattermost hay un canal con credenciales de despliegue. Con la cuenta `jaeger` se accede por SSH y se lee `user.txt`.

## Movimiento lateral

`jaeger` puede ejecutar un binario como `deploy`:

```bash
sudo -l
sudo -u deploy /home/deploy/password-manager
```

El programa pide una contraseña maestra y compara con una cadena almacenada. El binario se copia y se inspecciona:

```bash
scp jaeger@shoppy.htb:/home/deploy/password-manager .
strings -el password-manager
```

`strings -el` muestra la cadena UTF-16 `Sample`. Al introducirla, el programa imprime las credenciales de `deploy` y `su deploy` permite cambiar de cuenta.

## Escalada de privilegios

`deploy` está en el grupo `docker` y no hay contenedores en ejecución. El grupo permite montar el sistema de archivos del host:

```bash
docker run --rm -it -v /:/mnt alpine chroot /mnt sh
```

Dentro del contenedor se es root sobre el host y se puede leer `/root/root.txt` o añadir una clave SSH a `/root/.ssh/authorized_keys`. Otra vía es copiar una bash y darle SUID desde el propio contenedor.

## Evidencia

- Login con la expresión NoSQL y acceso al panel.
- Exportación de usuarios con el hash de `josh` y contraseña crackeada.
- Credenciales de `jaeger` en Mattermost y sesión SSH.
- Cadena `Sample` extraída con `strings -el` y credenciales de `deploy`.
- `deploy` en el grupo `docker` y lectura de archivos del host desde el contenedor.

## Lecciones aprendidas

- Las consultas NoSQL también aceptan operadores y expresiones booleanas.
- Un panel de administración no debe exportar hashes sin control adicional.
- La reutilización de contraseñas encadena servicios internos.
- `strings` debe probarse con anchos de 8 y 16 bits.
- Pertenecer al grupo `docker` equivale a root en el host.

## Mitigaciones y detección

- Validar tipos y rechazar operadores en los campos de autenticación.
- Usar hashing lento con sal para las contraseñas y limitar las exportaciones.
- No reutilizar credenciales entre aplicaciones y el sistema.
- Restringir el grupo `docker` y preferir un socket proxy con permisos mínimos.
- Monitorizar la creación de contenedores con `-v /:/` y montajes del host.
- Alertar de logins con comillas, operadores `$ne`/`$gt` o JSON inesperado.

## Referencias

- [0xdf — Shoppy](https://0xdf.gitlab.io/2023/01/14/htb-shoppy.html)
- [Hack The Box — Shoppy](https://app.hackthebox.com/machines/shoppy)
- [Knowledge — Inyección NoSQL](../../../knowledge/web/nosql-injection.md)
- [Knowledge — Escape de contenedor privilegiado](../../../knowledge/linux/docker-privileged-escape.md)
