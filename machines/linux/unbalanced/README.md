---
machine: Unbalanced
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, encfs, squid, xpath, pihole]
---

# Unbalanced — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`rsync` expone un backup cifrado con EncFS. Se crackea la contraseña, se monta y aparecen la configuración de Squid y credenciales. El proxy revela hosts internos; uno de ellos tiene una intranet con XPath injection que filtra usuarios y contraseñas. Con SSH se entra como `bryan`, se pivota al contenedor Pi-hole y un script con credenciales de root cierra la cadena.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
873/tcp   rsync
3128/tcp  squid
```

## Enumeración

- `rsync --list-only rsync://<IP>` muestra el módulo `conf_backups`.
- El módulo contiene `.encfs6.xml` y archivos con nombres cifrados.
- `encfs2john` y `john` recuperan la contraseña de EncFS.
- `squid.conf` revela `intranet.unbalanced.htb` y dos hosts internos.

## Foothold

Se descarga el backup, se crackea EncFS y se monta. La configuración de Squid permite usar el proxy y enumerar la caché, que revela las IPs `172.31.179.2` y `172.31.179.3`.

La intranet tiene un login vulnerable a XPath injection. Con una condición booleana se extraen usuarios y contraseñas; una de ellas da SSH como `bryan`.

```bash
rsync -a rsync://<IP>/conf_backups/ backup/
encfs2john backup/ > encfs.hash
john --wordlist=/usr/share/wordlists/rockyou.txt encfs.hash
encfs backup/ /mnt/decrypted
```

## Movimiento lateral

Como `bryan`, `ss` muestra dos puertos locales: 8080 y 5553. El 8080 corresponde al panel de Pi-hole en un contenedor. Se reenvía por SSH y se explota el panel para subir un webshell.

En el contenedor se encuentra un script de mantenimiento con la contraseña de root del host.

```bash
ssh -L 8080:127.0.0.1:8080 bryan@<IP>
```

## Escalada de privilegios

Se usa la contraseña encontrada en el script para `su` o SSH como root. La clave está en que el contenedor comparte un secreto que también es válido en el host.

```bash
su -
id
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un backup de configuración puede contener la clave de su propio cifrado.
- EncFS con contraseña débil no protege los datos.
- Squid sin autenticación expone la topología interna.
- Una XPath injection puede volcar credenciales completas.
- Los contenedores no deben compartir contraseñas con el host.

## Mitigaciones y detección

- Restringir `rsync` y no almacenar `.encfs6.xml` junto al backup.
- Usar contraseñas robustas y claves fuera del backup.
- Exigir autenticación en Squid y limitar ACLs.
- Parametrizar XPath y separar credenciales por servicio.

## Referencias

- [0xdf — Unbalanced](https://0xdf.gitlab.io/2020/12/05/htb-unbalanced.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+unbalanced)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+unbalanced+writeup)
