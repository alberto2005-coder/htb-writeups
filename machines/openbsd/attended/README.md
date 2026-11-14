---
machine: Attended
os: OpenBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [openbsd, smtp, vim, modeline, rop]
---

# Attended — Hack The Box (OpenBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

OpenSMTPD acepta correo de un remitente arbitrario y lo entrega a `guly`. Al abrir el mensaje, un modeline de Vim (CVE-2019-12735) ejecuta comandos. Un `.config.swp` revela la configuración SSH de `freshness`; desde ahí, un cron y el binario `authkeys` del gateway, vulnerable a un overflow, permiten ROP y root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh
25/tcp  smtp   OpenSMTPD
80/tcp  http   nginx
```

## Enumeración

- El puerto 25 acepta `MAIL FROM` y `RCPT TO` para usuarios locales.
- La entrega a `guly` es posible aunque el remitente no exista.
- El correo se procesa con Vim/Neovim y un modeline puede ejecutar comandos.
- La enumeración local muestra un `.config.swp` con la configuración SSH.

## Foothold

Se envía un correo con un modeline malicioso en el cuerpo. Al abrirlo, Vim interpreta `:!` y ejecuta una reverse shell como `guly`.

```bash
swaks --to guly@attended.htb --from freshness@attended.htb   --header 'Subject: hello' --body 'see attached'   --attach-type text/plain --attach @payload.txt --server <IP>
```

El payload usa `modeline` y `assert_fails()` para ejecutar el comando sin interacción.

## Movimiento lateral

En el home de `guly`, un `.config.swp` conserva la configuración SSH: `User freshness`, `ControlMaster` y la ruta del socket. Con esa información y la clave/agente disponible se abre SSH como `freshness`.

```bash
strings ~/.config.swp
ssh freshness@attended.htb
```

## Escalada de privilegios

`freshness` ejecuta un cron `fchecker.py` que procesa archivos de `/home/shared` y llama a `ssh -F <archivo>`. Un archivo controlado puede incluir opciones de SSH y ejecutar un comando local.

El siguiente salto es el gateway: `/home/freshness/authkeys` es un ELF de OpenBSD que `sshd` ejecuta como root y que sufre un desbordamiento de pila al parsear una clave RSA grande. Se construye un ROP para `execve("/usr/local/bin/python2", ...)` y se obtiene root en `attendedgw`.

```bash
cat /home/freshness/note.txt
file /home/freshness/authkeys
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un servidor de correo que acepta remitentes arbitrarios facilita el phishing interno.
- Los modelines de Vim son ejecución de código al abrir un archivo.
- Los archivos de intercambio de Vim filtran configuración y rutas.
- Un binario ejecutado por `sshd` como root es una superficie crítica.

## Mitigaciones y detección

- Exigir autenticación y validar remitentes en OpenSMTPD.
- Deshabilitar `modeline` o usar `securemodelines`.
- Limpiar archivos de intercambio y proteger directorios compartidos.
- Compilar `authkeys` con mitigaciones y validar el tamaño de las claves.

## Referencias

- [0xdf — Attended](https://0xdf.gitlab.io/2021/05/08/htb-attended.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+attended)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+attended+writeup)
