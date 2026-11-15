---
machine: Oz
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sqli, ssti, docker, port-knocking]
---

# Oz — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi y el crackeo de contraseñas abren una aplicación de tickets. Una SSTI de Jinja2 da una shell en un contenedor. La clave SSH se lee a través de una ruta montada por el contenedor de base de datos y se usa port knocking para alcanzar el host, donde Docker/Portainer permite escalar.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
sqlmap --url "http://oz.htb/tickets.php?id=1" --batch --dump
john hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt
# SSTI
curl -s "http://oz.htb/search?name={{7*7}}"
# Clave SSH en volumen
find / -name id_rsa 2>/dev/null
# Port knocking
knock <IP> 40809 50212 46969
ssh -i id_rsa <USER>@<IP>
# Docker
docker -H tcp://127.0.0.1:2375 ps
```

## Enumeración

- Aplicación de tickets con SQLi y usuarios con hashes débiles.
- Parámetros renderizados por Jinja2 dentro de un contenedor.
- Puertos del host filtrados y un servicio Docker/Portainer interno.

## Acceso inicial

La SQLi en la búsqueda de tickets filtra hashes; se crackean y se entra a la aplicación. Un campo de plantilla o nombre se renderiza con Jinja2 y permite ejecutar comandos en el contenedor.

## Escalada de privilegios

El contenedor de base de datos monta una ruta del host con la clave SSH de un usuario. Se lee la clave y se usa port knocking para abrir SSH; ya en el host, Docker/Portainer mal protegido permite montar `/` y ejecutar como root.

## Evidencia

- Hashes crackeados y acceso a tickets.
- SSTI con shell en el contenedor.
- Clave SSH, secuencia de knocking y contenedor privilegiado.

## Lecciones aprendidas

- La SSTI en un contenedor no es el final de la cadena.
- Los volúmenes de Docker exponen rutas del host.
- El port knocking no sustituye la autenticación.

## Mitigación y detección

- Parametrizar SQL y no renderizar plantillas con entrada.
- Revisar volúmenes y permisos de Docker.
- Proteger Portainer y limitar el socket Docker.

## Referencias

- [0xdf — Oz](https://0xdf.gitlab.io/2019/01/12/htb-oz.html)
- [Port knocking — knockd](https://manpages.debian.org/testing/knockd/knockd.8.en.html)
- [Hack The Box — Oz](https://app.hackthebox.com/machines/oz)
