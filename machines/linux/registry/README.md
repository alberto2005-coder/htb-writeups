---
machine: Registry
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, docker-registry, bolt-cms, restic, privesc]
---

# Registry — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un registro Docker privado con credenciales débiles permite descargar la imagen de Bolt CMS. La imagen contiene una clave SSH y una contraseña para `bolt`; Bolt 3.6.4 permite subir un webshell y pasar a `www-data`. `www-data` puede ejecutar `restic backup` como root, y se hace una copia de `/root` para leer el flag y la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
wfuzz -u http://registry.htb -H 'Host: FUZZ.registry.htb' -w subdomains.txt
```

- `22` SSH, `80`/`443` nginx.
- Los vhosts `docker.registry.htb` y `bolt.registry.htb` aparecen con `wfuzz`.
- El certificado TLS revela `docker.registry.htb`.

## Enumeración

El registro responde en `/v2/` y `/v2/_catalog` con credenciales débiles. Se lista `bolt-image`, se descarga el manifiesto y las capas, y se extrae el sistema de archivos.

```bash
curl -k --user <USER>:<PASS> https://docker.registry.htb/v2/_catalog
curl -k --user <USER>:<PASS> https://docker.registry.htb/v2/bolt-image/manifests/latest
```

## Foothold

Dentro de las capas hay una clave SSH y una contraseña para `bolt`. Se entra por SSH.

```bash
ssh -i bolt.key bolt@registry.htb
```

## Movimiento lateral

`/bolt` ejecuta Bolt CMS 3.6.4. El panel permite autenticarse con las credenciales encontradas; una vulnerabilidad de subida/ejecución permite colocar un webshell y obtener `www-data`.

```bash
curl 'http://registry.htb/bolt/files/shell.php?cmd=id'
```

## Escalada de privilegios

`www-data` puede ejecutar `restic backup` como root:

```bash
sudo /usr/bin/restic backup -r rest0xdf /root/root.txt
```

Se crea un repositorio local, se hace backup de `/root/root.txt` y de `/root/.ssh/id_rsa`, y se leen con `restic dump`. La clave permite entrar como root.

```bash
restic -r /tmp/restic/0xdf dump latest /root/root.txt
```

## Evidencia

- Registro Docker y credenciales débiles.
- Imagen con clave SSH y contraseña de `bolt`.
- Bolt CMS y webshell.
- `restic backup` como root.
- Backup de `/root` y root.

## Lecciones aprendidas

- Un registro Docker privado puede filtrar secretos de la imagen.
- Las imágenes incluyen claves y credenciales de despliegue.
- Bolt CMS antiguo permite ejecución mediante subida.
- Un `restic` sudo mal limitado copia archivos arbitrarios como root.

## Mitigación y detección

- Autenticar el registro y evitar credenciales por defecto.
- No incluir secretos en imágenes; usar secretos externos.
- Actualizar Bolt CMS y validar subidas.
- Restringir `restic` a rutas y repositorios concretos.

## Referencias

- [0xdf — Registry](https://0xdf.gitlab.io/2020/04/04/htb-registry.html)
- [IppSec — Registry](https://www.youtube.com/watch?v=w0h0QYswFNA)
- [Hack The Box — Registry](https://app.hackthebox.com/machines/registry)
