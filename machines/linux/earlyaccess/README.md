---
machine: EarlyAccess
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, sqli, second-order, lfi, docker, password-reuse, capabilities]
---

# EarlyAccess — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tres vhosts comparten la misma IP: `earlyaccess.htb`, `game.earlyaccess.htb` y `dev.earlyaccess.htb`. El registro del sitio principal no sanea el nombre de usuario, así que un XSS almacenado roba la cookie del administrador. Con esa sesión se accede al juego y a `validate.py`, el validador de claves que permite generar una clave válida. La clave abre el sitio de desarrollo, donde una SQLi de segundo orden (el nombre se guarda y se usa después en una consulta) vuelca hashes que se crackean. El LFI de `hash.php` y el poisoning de logs dan RCE como `www-data` en el contenedor web. La reutilización de contraseñas lleva a `www-adm`, después a `drew` en el host (su `.wgetrc` guarda credenciales de la API de claves) y a `game-tester` en el servidor del juego. Root en ese servidor se consigue provocando un crash; con el hash de `game-adm` se hace `su` en el host y una capacidad sobre `arp` permite leer la clave de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22` OpenSSH 7.9p1 Debian 10+deb10u2.
- `80` y `443` Apache httpd 2.4.38 (Debian).
- El certificado de `443` revela el dominio `earlyaccess.htb`.

```bash
ffuf -u https://earlyaccess.htb -H "Host: FUZZ.earlyaccess.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

Aparecen `game` y `dev`. Los tres se añaden a `/etc/hosts`.

## Enumeración

El sitio principal tiene home, mensajería, foro, tienda, registro de claves y perfil. El registro acepta nombres de usuario con caracteres especiales y el perfil los refleja sin escapar.

La mensajería y el foro permiten enviar contenido a otros usuarios; el administrador revisa el perfil y los mensajes, así que un XSS almacenado en el nombre se ejecuta en su navegador. Un servidor propio recibe la petición con la cookie de sesión.

Con la cookie del administrador se accede a las funciones privadas y al panel donde se generan claves del juego.

## Foothold

`game.earlyaccess.htb` permite descargar `validate.py`, un validador de claves con el formato:

```text
AAAAA-BBBBB-CCCC1-DDDDD-1234
```

El script comprueba los grupos y el dígito final, y se puede reproducir para generar una clave válida. Al introducirla en el perfil, la cuenta obtiene acceso al sitio de desarrollo.

En `dev.earlyaccess.htb` el nombre de usuario se guarda al registrarse y se inserta sin parametrizar en una consulta posterior: es una SQLi de segundo orden. Con una UNION se extraen los hashes de la tabla de usuarios:

```bash
sqlmap -u "https://dev.earlyaccess.htb/<RUTA>" --data="<PARAMETROS>" --batch --dump
hashcat -m 0 hashes /usr/share/wordlists/rockyou.txt
```

Las contraseñas crackeadas dan acceso al panel de desarrollo. `hash.php` incluye archivos según un parámetro y permite leer el código y, con poisoning de logs o de sesión, escribir una webshell en el contenedor web:

```bash
curl -s "https://dev.earlyaccess.htb/hash.php?file=../../../../var/log/apache2/access.log"
```

## Movimiento lateral

La webshell corre como `www-data` dentro de un contenedor Docker. La enumeración muestra la red interna y los archivos de configuración, con credenciales de `www-adm`. Esa contraseña se reutiliza para entrar por SSH al host como `www-adm`.

El home de `drew` contiene un `.wgetrc` con credenciales de la API de verificación de claves del juego. Con ellas se consulta la API, que devuelve la contraseña de `drew`; por SSH se llega a su cuenta y a `game-tester` en el servidor del juego.

## Escalada de privilegios

En el servidor del juego, el binario escucha en local y procesa las partidas. Un valor malformado provoca un crash que deja una shell como root de ese contenedor. Desde ahí se lee el hash de `game-adm` en el host, se crackea y se usa con `su`.

`game-adm` pertenece al grupo `adm`, que da acceso a logs y al binario `arp`. El binario tiene una capacidad que permite leer archivos con privilegios:

```bash
getcap -r / 2>/dev/null
/usr/sbin/arp -v -f /root/root.txt
cat /root/.ssh/id_rsa
```

Con la clave privada de root se cierra la máquina.

## Evidencia

- Nombre de usuario con XSS y cookie de administrador recibida.
- Clave de juego generada a partir de `validate.py`.
- UNION en el sitio de desarrollo y hashes crackeados.
- Webshell en el contenedor y credenciales de `www-adm`.
- `.wgetrc` de `drew` y API de claves consultada.
- Crash del servidor del juego y `su` como `game-adm`.
- `getcap` sobre `arp` y clave de root leída.

## Lecciones aprendidas

- Un XSS almacenado en un campo que solo revisa el administrador sigue siendo una vía de entrada.
- Las SQLi de segundo orden no aparecen en la petición que las provoca.
- Un LFI se convierte en RCE con logs o sesiones escribibles.
- La reutilización de contraseñas encadena contenedores y hosts sin exploits.
- Los binarios con capacidades son una escalada silenciosa frente a SUID.

## Mitigaciones y detección

- Escapar y validar todos los campos que se reflejan, incluidos nombres de usuario y perfiles.
- Parametrizar todas las consultas, también las que se ejecutan en pasos posteriores.
- No incluir archivos por ruta del usuario; usar listas de plantillas.
- Rotar contraseñas entre servicios y no guardarlas en `.wgetrc` ni en repositorios.
- Revisar `getcap -r /` periódicamente y retirar capacidades innecesarias.
- Alertar de crashes de servicios y de lecturas de `/root` desde procesos con capacidades.

## Referencias

- [0xdf — EarlyAccess](https://0xdf.gitlab.io/2022/02/12/htb-earlyaccess.html)
- [IppSec — EarlyAccess](https://www.youtube.com/watch?v=P4KLqTORmIw)
- [Hack The Box — EarlyAccess](https://app.hackthebox.com/machines/earlyaccess)
