---
machine: CrossFitTwo
os: OpenBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [openbsd, sqli, nodejs, yubikey, changelist]
---

# CrossFitTwo — Hack The Box (OpenBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio de empleados usa un WebSocket con SQLi; a través de un proxy Flask se leen archivos y credenciales. Un vhost Express carga módulos desde un directorio escribible, lo que permite ejecutar código como otro usuario. El binario SUID `log` lee backups de `changelist` con la clave SSH de root y el material de una Yubikey; ambos factores abren SSH como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh
80/tcp  http   nginx / relayd
5000/tcp http  Express (interno)
9999/tcp http  relayd (interno)
```

## Enumeración

- `employees.crossfit.htb` y `crossfit-club.htb` son vhosts distintos.
- El WebSocket de empleados refleja consultas SQL y permite UNION.
- Un proxy Flask local facilita el uso de `sqlmap` contra el WebSocket.
- La lectura de archivos revela credenciales y rutas de la aplicación.

## Foothold

Se confirma la inyección con una consulta booleana y se automatiza con `sqlmap` a través del proxy. La base de datos entrega credenciales de `david`, que permiten SSH.

```bash
sqlmap -r ws.request --technique=U --batch --timeout 3 --ignore-timeouts
ssh david@crossfit.htb
```

## Movimiento lateral

`david` pertenece al grupo `sysadmins`, que puede escribir en `/opt/sysadmin`. El vhost `crossfit-club.htb` ejecuta Express y un cron borra `/opt/sysadmin/node_modules` cada cinco minutos.

Antes del borrado se coloca un módulo `ws` o `log-to-file` malicioso en la ruta de búsqueda. Al reiniciarse el proceso, Node carga el módulo controlado y ejecuta código como `john`.

```bash
find /opt/sysadmin -maxdepth 3 -ls
```

## Escalada de privilegios

`/usr/local/bin/log` es SUID root y del grupo `staff`. Lee archivos de backup y permite acceder a `/var/backups`, donde `changelist` conserva copias de `/root/.ssh/id_rsa` y de `/var/db/yubikey/root.*`.

Se extrae la clave privada de root y se generan códigos Yubikey con la clave, UID y contador. `sshd` exige autenticación por clave y por contraseña, así que se usa la clave y el OTP como segundo factor.

```bash
log /var/backups/root_.ssh_id_rsa.current
log /var/backups/var_db_yubikey_root.key.current
ssh -i root.key root@crossfit.htb
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un WebSocket puede ser tan inyectable como un formulario HTTP.
- La resolución de módulos Node desde directorios escribibles es RCE.
- Los backups de `changelist` pueden conservar claves y secretos de autenticación.
- La autenticación multifactor no sirve si ambos factores están en el mismo host.

## Mitigaciones y detección

- Parametrizar consultas y validar el origen del WebSocket.
- Montar `/opt/sysadmin` sin escritura y fijar `NODE_PATH`.
- Proteger `/var/backups` y excluir claves privadas de `changelist`.
- Guardar los secretos Yubikey fuera del host y rotarlos.

## Referencias

- [0xdf — CrossFitTwo](https://0xdf.gitlab.io/2021/08/14/htb-crossfittwo.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+crossfittwo)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+crossfittwo+writeup)
