---
machine: Mentor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, api, docker, jwt, privesc]
---

# Mentor — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP con la comunidad `internal` filtra credenciales de la API. La API permite autenticarse como `james` y ejecutar comandos dentro de un contenedor. El contenedor corre uvicorn con `--reload`, así que se edita un modelo para exponer los hashes; se crackea el de `svc` y se entra por SSH. En `snmpd.conf` queda la contraseña del usuario bootstrap, que se reutiliza para `james`, y `james` puede ejecutar `/bin/sh` como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,161 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04, `80/tcp` una API HTTP y `161/udp` SNMP.
- `snmpwalk -v2c -c public` revela el nombre `mentor` y el contacto del servicio.
- La API vive en `mentorquotes.htb` y documenta endpoints de autenticación y citas.

## Enumeración

- `snmpbrute.py` encuentra la comunidad `internal`, con más permisos que `public`.
- `snmpwalk` con `internal` filtra credenciales de la API para `james`.
- El login devuelve un JWT; los endpoints permiten crear citas y ejecutar una acción interna.

## Foothold

Se obtiene un JWT como `james` y se abusa del endpoint de creación para inyectar un comando. La reverse shell cae como root dentro de un contenedor Docker.

```bash
curl -s -X POST http://mentorquotes.htb/api/v1/auth/authenticate -H 'Content-Type: application/json' -d '{"username":"james","password":"<PASSWORD>"}'
nc -lnvp 443
```

## Movimiento lateral

El contenedor ejecuta uvicorn con `--reload` y monta `/app`. Se añade `password` al modelo `userDB`, se consulta la API y se obtienen los hashes. El de `svc` se crackea y sirve para SSH en el host.

## Escalada de privilegios

`/etc/snmp/snmpd.conf` contiene la contraseña del usuario bootstrap de SNMPv3. Esa contraseña se reutiliza para `james`, que puede ejecutar `/bin/sh` con sudo.

```bash
cat /etc/snmp/snmpd.conf | grep -v '^#' | grep .
su james -
sudo -l
sudo /bin/sh
```

## Evidencia

- Comunidad SNMP `internal` y credenciales de la API.
- Shell root en el contenedor y hashes expuestos por el modelo.
- SSH como `svc` y `sudo /bin/sh` como `james`.

## Lecciones aprendidas

- SNMP puede filtrar más que métricas: credenciales y configuración.
- `--reload` en producción permite cambios de código persistentes.
- Las contraseñas de bootstrap se reutilizan entre servicios.

## Mitigación y detección

- Restringir SNMP y usar comunidades fuertes o SNMPv3.
- No usar `--reload` ni montar código escribible en producción.
- Rotar contraseñas de bootstrap y limitar `sudo` a comandos concretos.

## Referencias

- [0xdf — Mentor](https://0xdf.gitlab.io/2023/03/11/htb-mentor.html)
- [IppSec — Mentor](https://www.youtube.com/watch?v=MjddXhMF9vg)
- [Hack The Box — Mentor](https://app.hackthebox.com/machines/mentor)
