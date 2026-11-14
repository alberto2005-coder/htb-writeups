---
machine: Schooled
os: FreeBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [freebsd, moodle, xss, deserialization, package-manager]
---

# Schooled — Hack The Box (FreeBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Moodle encadena XSS, suplantación de profesor y una vulnerabilidad de roles hasta instalar un plugin con webshell. La base de datos entrega hashes bcrypt, uno se crackea y da SSH como `jamie`. `pkg` con permisos de root y un `/etc/hosts` escribible permiten servir un paquete FreeBSD malicioso y ejecutar `+POST_INSTALL` como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh     OpenSSH 7.9 (FreeBSD)
80/tcp    http    Apache httpd 2.4.46 (FreeBSD) PHP/7.4.15
33060/tcp mysqlx  MySQL X Protocol
```

## Enumeración

- El vhost `moodle.schooled.htb` sirve un Moodle antiguo con registro abierto.
- La versión y los plugins se confirman desde `config.php` y la respuesta HTTP.
- Un usuario recién registrado puede matricularse como profesor en un curso.
- El perfil del profesor refleja entrada sin sanear y ejecuta JavaScript en el navegador del administrador.

## Foothold

La XSS se usa para crear o modificar una cuenta con rol de manager. Después se abusa de la gestión de roles de Moodle (CVE-2020-14321) para asignar privilegios de administrador a la cuenta controlada.

Con acceso administrativo se instala un plugin malicioso. El ZIP se construye con un webshell en el bloque de versión y se sube desde la interfaz; al visitar la ruta del plugin se ejecuta código como `www`.

```bash
curl -s -b cookie.txt 'http://moodle.schooled.htb/moodle/blocks/leaflet/version.php?c=id'
```

## Movimiento lateral

`config.php` contiene las credenciales de la base de datos. La tabla de usuarios guarda hashes bcrypt; se extraen y se atacan con `hashcat` contra una wordlist. Uno de los hashes corresponde a `jamie`, que reutiliza la contraseña para SSH.

```bash
mysql -u moodle -p'<DB_PASSWORD>' moodle -e 'select username,password from mdl_user;'
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh jamie@schooled.htb
```

## Escalada de privilegios

`jamie` puede ejecutar `pkg update` y `pkg install *` con privilegios de root, y puede escribir `/etc/hosts`. Se cambia `devops.htb` por la IP del atacante, se publica un repositorio `pkg` mínimo y se instala un paquete propio.

El paquete incluye `+MANIFEST`, `plist` y `+POST_INSTALL`; este último se ejecuta como root durante la instalación.

```bash
sudo -l
sudo pkg update
sudo pkg install -y <PACKAGE_NAME>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- La XSS contra un administrador vale tanto como un token de sesión.
- La asignación de roles debe validarse en servidor, no solo en la interfaz.
- Un repositorio de paquetes sin firma convierte `pkg` en ejecución de código.
- Escribir `/etc/hosts` permite redirigir el repositorio legítimo.

## Mitigaciones y detección

- Actualizar Moodle y restringir la instalación de plugins a administradores de confianza.
- Validar roles y capacidades en cada petición.
- Firmar repositorios `pkg` y bloquear cambios en `/etc/hosts`.
- Registrar instalaciones de plugins y ejecuciones de `pkg` fuera de mantenimiento.

## Referencias

- [0xdf — Schooled](https://0xdf.gitlab.io/2021/09/11/htb-schooled.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+schooled)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+schooled+writeup)
