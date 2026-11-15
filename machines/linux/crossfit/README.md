---
machine: CrossFit
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, xss, csrf, ftp, ansible, php-shellcommand, cron, privesc]
---

# CrossFit — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un XSS en el user-agent llega al bot administrador; CORS revela un subdominio FTP y un CSRF crea una cuenta. Con FTP se sube un webshell y se obtiene `www-data`. Un hash de Ansible se crackea para `hank`, y un plugin `php-shellcommand` inyecta comandos para `isaac`. Un binario de cron con escritura arbitraria y un symlink predecible escriben en `authorized_keys` de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` FTP, `22` SSH y `80` Apache con `crossfit.htb`.
- `wfuzz` encuentra `ftp.crossfit.htb` y `admin.crossfit.htb`.
- El sitio principal tiene un formulario de reporte que registra el user-agent.

## Enumeración

- Un payload XSS en el user-agent se ejecuta en el navegador del administrador.
- Desde allí se consulta `ftp.crossfit.htb`; CORS permite leer la respuesta.
- Se obtiene el token CSRF y se crea una cuenta FTP con una petición cross-site.

## Foothold

La cuenta FTP permite subir un webshell PHP al directorio servido. Se visita y se obtiene `www-data`.

```bash
curl 'http://crossfit.htb/uploads/shell.php?cmd=id'
```

## Movimiento lateral

`/etc/ansible/playbooks/adduser_hank.yml` contiene el hash de `hank`. Se crackea con Hashcat y se usa para `su hank`; `hank` pertenece a `admins`, lo que permite leer el directorio `send_updates` de `isaac`.

```bash
hashcat -m 1800 hank.hash rockyou.txt
su hank
```

El plugin `php-shellcommand` de `send_updates` concatena un parámetro en una llamada al sistema. Se inyecta un comando desde la base de datos y se obtiene `isaac`.

## Escalada de privilegios

Un cron ejecuta `/bin/dbmsg` como root. El binario lee mensajes de MySQL, calcula un nombre en `/var/local` con `rand()` y escribe tres campos; el nombre se puede predecir porque el cron corre en un segundo fijo. Se crea un symlink de ese nombre hacia `/root/.ssh/authorized_keys` y se inserta la clave pública en la base.

```bash
ln -s /root/.ssh/authorized_keys /var/local/<HASH>
```

## Evidencia

- XSS en user-agent y bot admin.
- CORS, CSRF y cuenta FTP.
- Webshell y `www-data`.
- Hash de Ansible y `hank`.
- `php-shellcommand` e `isaac`.
- `dbmsg`, symlink y root.

## Lecciones aprendidas

- El user-agent es un canal XSS si se muestra en un panel.
- CORS mal configurado permite leer subdominios internos.
- Los playbooks de Ansible guardan hashes reutilizables.
- Un cron con nombres predecibles y symlinks es escritura arbitraria.

## Mitigación y detección

- Escapar el user-agent y usar CSP.
- Restringir CORS a orígenes explícitos.
- No guardar hashes en playbooks; usar vault.
- Evitar symlinks y nombres predecibles en scripts root.

## Referencias

- [0xdf — CrossFit](https://0xdf.gitlab.io/2021/03/20/htb-crossfit.html)
- [IppSec — CrossFit](https://www.youtube.com/watch?v=Z3Lj_YN0crc)
- [Hack The Box — CrossFit](https://app.hackthebox.com/machines/crossfit)
