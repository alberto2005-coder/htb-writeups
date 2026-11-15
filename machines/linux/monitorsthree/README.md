---
machine: MonitorsThree
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, cacti, sqli, duplicati, privesc]
---

# MonitorsThree — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El reset de contraseña de la web principal es inyectable y filtra el hash del administrador, que se crackea. Esas credenciales abren Cacti 1.2.26, vulnerable a CVE-2024-25642: la importación de paquetes permite subir un PHP y obtener `www-data`. La base de Cacti entrega la contraseña de `marcus`, que puede acceder a Duplicati; un backup del filesystem de root permite leer la flag o escribir una clave SSH.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` la web de MonitorsThree.
- `ffuf` con `Host: FUZZ.monitorsthree.htb` descubre `cacti.monitorsthree.htb`.
- El puerto 8084 aparece filtrado y no responde al inicio.

## Enumeración

- `/forgot_password.php` concatena el usuario en la consulta.
- Un `UNION` devuelve el hash MD5 del administrador y su email.
- El hash se crackea y las mismas credenciales funcionan en Cacti.

```bash
sqlmap -u 'http://monitorsthree.htb/forgot_password.php' --data 'username=admin' --batch --dump
```

## Foothold

Cacti 1.2.26 es vulnerable a CVE-2024-25642. Se genera un paquete malicioso, se importa desde `Import/Export` y el PHP se escribe en `resource/`, donde se ejecuta.

```bash
php cve-2024-25642.php
curl 'http://cacti.monitorsthree.htb/cacti/resource/<FILE>.php'
```

## Movimiento lateral

La configuración de Cacti contiene credenciales de la base; en `user_auth` está el hash de `marcus`. Se crackea y se usa para SSH. `marcus` tiene un túnel al puerto de Duplicati.

```bash
ssh -L 8200:127.0.0.1:8200 marcus@<IP>
```

## Escalada de privilegios

Duplicati se ejecuta como root y permite crear un backup de `/`. Se restaura en una ruta controlada para leer `/root/root.txt`, o se añade una clave pública a `/root/.ssh/authorized_keys` y se entra por SSH.

```text
Source: /root
Target: /tmp/restore
```

## Evidencia

- SQLi en el reset y hash de administrador.
- Cacti 1.2.26 y CVE-2024-25642.
- Contraseña de `marcus` y túnel a Duplicati.
- Backup de root y clave SSH.

## Lecciones aprendidas

- Un reset de contraseña puede ser un SQLi con ECO.
- La importación de paquetes de Cacti ejecuta contenido si no se valida.
- Una herramienta de backup con root y una interfaz local es una escalada directa.

## Mitigación y detección

- Parametrizar el reset y usar tokens de un solo uso.
- Actualizar Cacti y restringir la importación de paquetes.
- Ejecutar Duplicati sin root y aislar su interfaz.

## Referencias

- [0xdf — MonitorsThree](https://0xdf.gitlab.io/2025/01/18/htb-monitorsthree.html)
- [IppSec — MonitorsThree](https://www.youtube.com/watch?v=4y2gp_GTBqQ)
- [Hack The Box — MonitorsThree](https://app.hackthebox.com/machines/monitorsthree)
