---
machine: Moderators
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, upload-bypass, wordpress, virtualbox, luks, hashcat, privesc]
---

# Moderators — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un parámetro `report` en `reports.php` permite enumerar reportes por ID; al recorrerlos se llega a la página de subida. El filtro exige PDF, pero se evade cambiando el MIME, los magic bytes y el nombre a `htb.pdf.php`; `popen` no está bloqueada y da shell como `www-data`. En localhost hay un WordPress interno: el plugin Brandfolder permite pasar a `lexi`, y con el `wp-config.php` se obtiene la contraseña de MySQL. Otra base de datos contiene secretos cifrados por el plugin passwords-manager; el análisis del código permite descifrarlos y obtener la clave SSH de `john`. En su home hay una VM VirtualBox (`2019.vdi`) con cifrado de disco y LUKS; tras romper ambas capas aparece una contraseña que funciona para `sudo`, y `john` tiene `(root) ALL`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: Apache httpd 2.4.41.

```bash
echo '<IP> moderators.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://moderators.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio tiene reportes con `reports.php?report=<ID>`. Con `wfuzz` se recorren los IDs y se localiza la página de subida; el WordPress interno aparece después, desde la shell.

La enumeración de puertos locales muestra servicios web y bases de datos que no son accesibles desde fuera; se usa un túnel para llegar a ellos.

## Foothold

La página de subida exige un PDF y valida MIME, magic bytes y extensión. Se envía `Content-Type: application/pdf`, se antepone `%PDF-` al contenido y se usa el nombre `htb.pdf.php`; así pasa el filtro y el servidor ejecuta el `.php` final. La webshell se ejecuta, aunque `disable_functions` bloquea `system`, `exec`, `shell_exec` y `passthru`; `popen` no está bloqueada, así que se usa para lanzar la reverse shell y obtener shell como `www-data`.

## Movimiento lateral

En localhost corre un WordPress (`site.new`). El plugin Brandfolder tiene una vulnerabilidad que permite leer archivos o ejecutar acciones con privilegios del sitio; se explota para obtener acceso como `lexi`. Su grupo da acceso a `wp-config.php`, con las credenciales de MySQL.

Con MySQL se accede a la base del WordPress y a los secretos del plugin passwords-manager. El código del plugin muestra el cifrado y la clave; se descifran los registros y aparece la clave SSH de `john`. Se entra por SSH como `john`.

## Escalada de privilegios

`john` tiene scripts y una VM VirtualBox en su home: `2019.vdi` y `2019-08-01.vbox`. El disco está cifrado por VirtualBox y, dentro, por LUKS. Se extrae el material cifrado y se rompe la contraseña de VirtualBox con `pyvboxdie-cracker` (o con el hash que genera `virtualbox2hashcat.py`). Para LUKS, Hashcat no soporta LUKS2 en esa versión, así que la frase se prueba localmente con `cryptsetup luksOpen --test-passphrase`. La contraseña resultante funciona para `sudo`.

```bash
python3 pyvboxdie-cracker.py -v 2019-08-01.vbox -d /usr/share/wordlists/rockyou.txt
sudo -l
sudo -i
```

`sudo -l` confirma `(root) ALL` para `john`, así que `sudo -i` cierra la máquina.

## Evidencia

- Enumeración de reportes por ID y localización de la página de subida.
- Webshell `htb.pdf.php` ejecutada pese al filtro y a `disable_functions`.
- WordPress interno y plugin Brandfolder.
- `wp-config.php` con credenciales de MySQL.
- Secretos del plugin passwords-manager descifrados y clave SSH de `john`.
- VDI con cifrado VirtualBox y LUKS roto.
- `sudo -l` con `(root) ALL` y `id` con UID 0.

## Lecciones aprendidas

- Un IDOR de reportes permite enumerar la aplicación y encontrar funciones internas.
- Los filtros de subida basados en listas negras se evaden.
- `disable_functions` no equivale a aislamiento; siempre quedan vías de ejecución.
- Los plugins de WordPress y sus bases de datos acumulan secretos.
- Una VM de desarrollo puede contener credenciales de producción.
- VirtualBox y LUKS se pueden romper si la contraseña es débil.

## Mitigaciones y detección

- No usar nombres de archivo controlados por el usuario; mapear IDs a rutas.
- Validar subidas por contenido y extensión permitida, y guardar fuera del webroot.
- Restringir `disable_functions` junto con `open_basedir` y un usuario sin privilegios.
- Auditar plugins de WordPress y sus credenciales; rotar las de MySQL.
- No guardar VMs con credenciales en homes de usuarios.
- Usar contraseñas robustas para VirtualBox y LUKS; monitorizar `sudo` y montajes.

## Referencias

- [0xdf — Moderators](https://0xdf.gitlab.io/2022/11/05/htb-moderators.html)
- [IppSec — Moderators](https://www.youtube.com/watch?v=V70gFSoh3aU)
- [Hack The Box — Moderators](https://app.hackthebox.com/machines/moderators)
- [Knowledge — VirtualBox, VDI y LUKS](../../../knowledge/forensics/virtualbox-vdi-luks.md)
