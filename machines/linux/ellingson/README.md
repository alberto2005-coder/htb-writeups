---
machine: Ellingson
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, flask, werkzeug, debugger, shadow, hashcat, suid, buffer-overflow, rop]
---

# Ellingson — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Flask deja el depurador de Werkzeug accesible en la web. La consola permite ejecutar comandos, y como la salida hacia fuera está bloqueada, se usa para escribir una clave pública en `authorized_keys` y entrar por SSH como `hal`. `hal` pertenece al grupo `adm` y puede leer `shadow.bak`; el crackeo de los hashes da la contraseña de `margo`. `margo` encuentra el SUID `/usr/bin/garbage`, un binario con desbordamiento de buffer, sin canary ni PIE pero con NX y ASLR. La explotación es un ROP de 64 bits: fuga de libc, cálculo de offsets y segunda etapa con `one_gadget` para root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 7.6p1 Ubuntu.
- `80`: nginx 1.14.0 sirviendo una aplicación Flask.

```bash
echo '<IP> ellingson.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://ellingson.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio tiene artículos y un buscador. Al provocar un error en una ruta de artículo aparece la página del depurador de Werkzeug, con el aviso de que no es seguro. La consola interactiva se habilita con `__debugger__=yes` y el secreto que aparece en la propia página; desde ahí se ejecutan comandos de Python en el servidor.

La enumeración del sistema muestra los usuarios `hal` y `margo`, y un servicio SSH. Los intentos de reverse shell fallan, lo que sugiere un firewall de salida.

## Foothold

Como la conexión inversa no funciona, se aprovecha el depurador para escribir una clave pública en `/home/hal/.ssh/authorized_keys`:

```text
__debugger__=yes&cmd=open('/home/hal/.ssh/authorized_keys','a').write('<PUBLIC_KEY>\n')
```

Después se entra por SSH como `hal` y se retira la clave añadida.

## Movimiento lateral

`id` muestra que `hal` está en el grupo `adm`, con acceso a logs y a copias de respaldo. Entre los archivos aparece `shadow.bak`, una copia del archivo de hashes. Se copia y se crackea con `hashcat` o `john`; el hash de `margo` se rompe y su contraseña permite `su` o SSH.

```bash
id
find / -group adm -type f 2>/dev/null
cat /var/backups/shadow.bak
hashcat -m 1800 hashes.txt /usr/share/wordlists/rockyou.txt
```

## Escalada de privilegios

`find / -perm -4000` muestra `/usr/bin/garbage`, un binario no estándar que pide una contraseña. Con una entrada larga provoca un segmentation fault. `checksec` indica:

```text
RELRO: Partial RELRO
Stack: No canary found
NX: NX enabled
PIE: No PIE (0x400000)
```

ASLR está activo (`/proc/sys/kernel/randomize_va_space` = 2). Al no haber canary ni PIE, se controla el retorno, pero NX impide ejecutar la pila. La cadena es:

1. Medir el offset con `pattern_create`/`pattern_offset`.
2. Usar un `puts`/`printf` de la PLT para filtrar una dirección de libc.
3. Calcular la base de libc y la dirección de `system` o de un `one_gadget`.
4. Enviar una segunda entrada con el ROP y obtener root.

```bash
checksec --file=./garbage
gdb -q ./garbage
pwn checksec ./garbage
ROPgadget --binary ./garbage | grep "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6
```

## Evidencia

- Página del depurador de Werkzeug y ejecución de `id` desde la consola.
- Clave añadida a `authorized_keys` y sesión SSH como `hal`.
- `shadow.bak` legible por el grupo `adm`.
- Hash de `margo` crackeado y `su` correcto.
- `checksec` del SUID `garbage` y crash con entrada larga.
- Fuga de libc, segunda etapa y `id` con UID 0.

## Lecciones aprendidas

- El depurador de Werkzeug nunca debe estar accesible en producción.
- Una copia de `shadow` con permisos laxos equivale a tener las contraseñas.
- Un binario SUID sin canary ni PIE sigue siendo explotable con NX y ASLR mediante ROP.
- La fuga de una dirección de libc es el paso que falta para derrotar ASLR.
- Los grupos `adm` y `sudo` deben revisarse como parte de la escalada.

## Mitigaciones y detección

- Deshabilitar `debug=True` y el depurador en producción; restringir `/console`.
- Proteger `shadow`, `shadow.bak` y los backups con permisos 640 y propietario root.
- Compilar con `-fstack-protector-strong`, PIE y RELRO completo.
- Retirar SUID innecesarios y auditar los que queden.
- Alertar de accesos a `/console`, `__debugger__` y de crashes de binarios SUID.
- Monitorizar la lectura de `shadow.bak` y los cambios en `authorized_keys`.

## Referencias

- [0xdf — Ellingson](https://0xdf.gitlab.io/2019/10/19/htb-ellingson.html)
- [IppSec — Ellingson](https://www.youtube.com/watch?v=XVYgBetSvS8)
- [Hack The Box — Ellingson](https://app.hackthebox.com/machines/ellingson)
- [Knowledge — SUID: desbordamiento de buffer por etapas](../../../knowledge/linux/suid-buffer-overflow.md)
