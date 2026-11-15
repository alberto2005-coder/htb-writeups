---
machine: Travel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, git, ssrf, memcached, php-deserialization, ldap]
---

# Travel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un repositorio `.git` expuesto revela el código de una aplicación RSS. Un SSRF permite envenenar memcached con un objeto PHP serializado y obtener un webshell en un contenedor. El hash de la base se crackea y da un usuario del host que administra LDAP; se modifican credenciales, clave SSH y grupo sudo para llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
git-dumper http://blog.travel.htb/.git/ repo
grep -R "memcache\|unserialize\|rss" repo
# SSRF a memcached
curl -s "http://blog.travel.htb/import?url=http://127.0.0.1:11211/"
# Webshell en el contenedor
curl -s http://blog.travel.htb/cache.php?cmd=id
# Hash y LDAP
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
ldapmodify -x -D "cn=admin,dc=travel,dc=htb" -w '<PASS>' -f change.ldif
```

## Enumeración

- `.git` accesible en el vhost del blog.
- Aplicación RSS con SSRF y memcached interno.
- Base de datos con hashes y LDAP administrado por un usuario del host.

## Acceso inicial

Se reconstruye el repositorio con `git-dumper` y se revisa el código: el importador RSS acepta URLs y usa memcached. Se envía una URL que apunta a memcached y se escribe una clave con un objeto PHP serializado que la aplicación deserializa, dando un webshell en el contenedor.

## Escalada de privilegios

El contenedor expone una base con hashes; se crackea uno y se obtiene SSH al host. Ese usuario administra LDAP: se cambia la contraseña de un usuario privilegiado, se añade una clave SSH y se incluye en `sudo`, y se entra como root.

## Evidencia

- Repositorio reconstruido desde `.git`.
- Clave en memcached y webshell en el contenedor.
- Hash crackeado, cambios LDAP y shell de root.

## Lecciones aprendidas

- `.git` expuesto entrega el código y sus secretos.
- SSRF hacia memcached puede inyectar objetos serializados.
- LDAP mal delegado permite cambiar identidades y privilegios.

## Mitigación y detección

- No publicar `.git` y revisar el despliegue.
- Aislar memcached y no deserializar datos de caché.
- Limitar quién administra LDAP y auditar cambios de grupos.

## Referencias

- [0xdf — Travel](https://0xdf.gitlab.io/2020/09/12/htb-travel.html)
- [Memcached — Protocol](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)
- [Hack The Box — Travel](https://app.hackthebox.com/machines/travel)
