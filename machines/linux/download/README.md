---
machine: Download
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, prisma, file-read, postgresql, tty, tiocsti, privesc]
---

# Download — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El endpoint `/files/download/<id>` es vulnerable a path traversal cuando la barra se codifica como `%2f`. La lectura de `app.js` revela la clave de firma de la cookie de sesión y el modelo Prisma. Un endpoint de login compara el SHA-1 de la contraseña con `startsWith`, lo que permite extraer el hash carácter a carácter y crackearlo; con SSH como `wesley` se llega a PostgreSQL. Escribiendo en el `.profile` de `postgres` y usando pushback de TTY (TIOCSTI) se inyectan comandos en la shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` nginx delante de una aplicación Node/Express.
- La aplicación permite subir archivos, verlos y descargarlos.
- `feroxbuster` no encuentra rutas ocultas: hacen falta los IDs completos.

## Enumeración

La cookie `download_session` es base64 más una firma HMAC-SHA1. Al añadir `%2f` al ID de descarga se lee `/etc/passwd` y, subiendo directorios, `package.json`, `app.js` y el resto del código. `app.js` contiene el secreto de `cookie-session` y el esquema Prisma.

## Foothold

El login compara `hash.startsWith(input)` sobre el SHA-1 de la contraseña, lo que actúa como oráculo de prefijos. Se automatiza la extracción del hash de `wesley` y se crackea con `hashcat -m 0`. La contraseña funciona por SSH.

```bash
curl --path-as-is 'http://<IP>/files/download/..%2f..%2f..%2fetc%2fpasswd'
hashcat -m 0 wesley.hash rockyou.txt
```

## Movimiento lateral

En `/etc/systemd/system/download-site.service` está `DATABASE_URL` con la contraseña de PostgreSQL. La base `download` y la tabla `User` confirman el hash obtenido. No hay más usuarios locales.

## Escalada de privilegios

Un script de gestión arranca como root, ejecuta `su -l postgres` y sale a una shell interactiva. Como `postgres` puede escribir su `.profile`, se usa `COPY ... TO` para dejarlo con un payload que llama a `TIOCSTI` sobre la TTY padre. Al terminar el `su`, root ejecuta lo que quedó en el buffer de entrada.

```sql
COPY (SELECT 'python3 -c "import fcntl,termios; ..."') TO '/var/lib/postgresql/.profile';
```

El payload encola `cp /bin/bash /tmp/root; chmod 6777 /tmp/root` y después se ejecuta `/tmp/root -p`.

## Evidencia

- Lectura de `app.js` con `%2f`.
- Extracción del hash mediante `startsWith`.
- `DATABASE_URL` en la unidad de systemd.
- `.profile` modificado y shell con UID 0.

## Lecciones aprendidas

- Decodificar la URL antes de validar rutas cambia por completo el resultado.
- Comparar hashes con prefijos filtra el valor completo.
- Los secretos de sesión en el código permiten forjar cookies.
- `su` interactivo y TTY pushback convierten una escritura como `postgres` en root.

## Mitigación y detección

- Resolver y canonicalizar la ruta, y comprobar que queda dentro del directorio de subidas.
- Comparar hashes en tiempo constante y sobre el valor completo.
- Sacar secretos del código y rotar `DATABASE_URL`.
- Restringir la escritura en homes de servicio y deshabilitar `TIOCSTI` (`dev.tty.legacy_tiocsti=0`).

## Referencias

- [0xdf — Download](https://0xdf.gitlab.io/2023/11/11/htb-download.html)
- [IppSec — Download](https://www.youtube.com/watch?v=UUn9x7mw1i0)
- [Hack The Box — Download](https://app.hackthebox.com/machines/download)
