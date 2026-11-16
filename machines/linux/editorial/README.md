---
machine: Editorial
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, git, gitpython, cve-2022-24439, privesc]
---

# Editorial — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La función de portada descarga una URL y guarda la respuesta, lo que permite un SSRF contra una API en localhost. La API filtra credenciales de `dev` por SSH; un repositorio Git en su home contiene una versión antigua con la contraseña de `prod`. `prod` puede ejecutar un script que usa GitPython 3.1.29, vulnerable a CVE-2022-24439, y el argumento `ext::` da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` nginx con una web de publicación.
- Formulario de subida de portada que acepta una URL y guarda una vista previa en `/static/uploads/<uuid>`.
- La web resuelve `editorial.htb`.

## Enumeración

Se apunta la URL al propio host y a `localhost` en distintos puertos. Un fuzzeo de puertos con `ffuf` descubre una API interna en `5000`. La respuesta se recupera del archivo estático; `/api/latest/metadata/messages/authors` contiene un mensaje de bienvenida con usuario y contraseña.

## Foothold

Las credenciales de `dev` funcionan por SSH. En `~/apps` hay un `.git` sin los archivos de trabajo; `git log` y `git diff` entre commits muestran el cambio de la contraseña de `prod` a la de `dev`, revelando la de `prod`.

```bash
# SSRF a la API interna
url=http://localhost:5000/api/latest/metadata/messages/authors
# CVE-2022-24439
sudo /usr/bin/python3 /opt/.../clone_prod_change.py 'ext::sh -c /dev/shm/root.sh'```

## Movimiento lateral

La contraseña de `prod` funciona por SSH. `prod` puede ejecutar como root `/opt/.../clone_prod_change.py`, que hace `Repo.clone_from(sys.argv[1], ...)`.

## Escalada de privilegios

GitPython 3.1.29 es vulnerable a CVE-2022-24439: al pasar una URL `ext::sh -c <comando>`, Git ejecuta el comando con `protocol.ext.allow=always`. Se apunta a un script escribible que copia bash y le da SUID, y se ejecuta con sudo.

## Evidencia

- SSRF a `localhost:5000`.
- Credenciales de `dev` en la API.
- `git diff` con la contraseña de `prod`.
- GitPython 3.1.29 y `ext::` como root.

## Lecciones aprendidas

- Una descarga de URL puede alcanzar servicios internos.
- Los repositorios Git conservan secretos aunque se borren los archivos.
- Las dependencias antiguas de GitPython permiten inyección de argumentos.
- Un script con sudo que acepta una URL es una frontera de confianza.

## Mitigación y detección

- Validar destinos y bloquear loopback en descargas.
- Rotar secretos y limpiar el historial de Git.
- Actualizar GitPython y deshabilitar `protocol.ext`.
- No ejecutar clones como root.

## Referencias

- [0xdf — Editorial](https://0xdf.gitlab.io/2024/10/19/htb-editorial.html)
- [IppSec — Editorial](https://www.youtube.com/watch?v=eggi_GQo9fk)
- [Hack The Box — Editorial](https://app.hackthebox.com/machines/editorial)
