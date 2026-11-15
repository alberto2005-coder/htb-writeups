---
machine: Rope
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, pwn, format-string, got, rop, privesc]
---

# Rope — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un servidor web propio en `9999` permite recorrer directorios y filtrar la dirección de `puts` con una cadena de formato. Se sobrescribe la GOT de `puts` con `system` y se ejecuta un comando. En local, el servicio `1337` se ejecuta como root y tiene canary, PIE y NX; se filtra la dirección y se monta una ROP para llamar a `system`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,9999 <IP>
```

- `22/tcp` OpenSSH y `9999/tcp` un servidor HTTP escrito en C, no nginx.
- La respuesta incluye cabeceras propias y un listado de directorios.
- `1337/tcp` solo escucha en localhost y ejecuta un binario con SUID/root.

## Enumeración

- `GET //etc/passwd` escapa del directorio raíz por la doble barra.
- Los logs del servidor pasan por `printf(user_input)`, lo que produce una cadena de formato.
- `checksec` del binario local muestra canary, PIE y NX; el servicio corre como root.

## Foothold

Se envía `%p` repetidamente y se localiza la dirección de `puts` en la GOT. Se escribe `system` con `%n` en dos mitades y se pide una ruta que contenga `; bash -c '...'`, que ahora se ejecuta como `system`.

```bash
python3 exploit.py --host <IP> --port 9999 --libc <LIBC>
# 1) leak puts, 2) calcular base, 3) escribir GOT, 4) disparar
```

## Movimiento lateral

No hay otro host. El movimiento es del servidor web al usuario `r1` y de ahí al binario local que corre como root.

## Escalada de privilegios

El binario de `1337` tiene un stack overflow con canary. Se filtra el canary y la base PIE, y se construye una ROP con `pop rdi; ret` hacia `/bin/sh` y `system`. Al conectarse al puerto local se obtiene una shell de root.

```bash
python3 r1.py --host 127.0.0.1 --port 1337
# leak canary + PIE, luego ROP: pop rdi; /bin/sh; system
```

## Evidencia

- `/etc/passwd` leído con `//`.
- GOT de `puts` sobrescrita y comando ejecutado.
- Canary/PIE filtrados y shell de root por `1337`.

## Lecciones aprendidas

- Pasar entrada del usuario a `printf` como formato es una vulnerabilidad crítica.
- Una escritura arbitraria en la GOT convierte una fuga en ejecución.
- Los servicios locales privilegiados son parte de la superficie de escalada.

## Mitigación y detección

- Usar `printf("%s", input)` y compilar con `-Wformat-security`.
- Habilitar RELRO completo, PIE y NX en todos los binarios.
- No ejecutar servicios de red locales como root; usar usuarios dedicados.

## Referencias

- [0xdf — Rope](https://0xdf.gitlab.io/2020/05/23/htb-rope.html)
- [IppSec — Rope](https://www.youtube.com/watch?v=GTQxZlr5yvE)
- [Hack The Box — Rope](https://app.hackthebox.com/machines/rope)
