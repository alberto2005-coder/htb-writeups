---
machine: Format
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, php, gitea, lfi, redis, nginx, ssti]
---

# Format — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un microblog PHP y su repositorio Gitea permiten revisar el código y encontrar lectura/escritura arbitraria de archivos. Una mala configuración de `proxy_pass` en Nginx deja Redis accesible por un socket Unix; se envenena la base para obtener el rol `pro`, se escribe una webshell en el directorio habilitado y se obtiene `www-data`. Las credenciales compartidas de Redis dan acceso a `cooper` y un script Python ejecutado como root con interpolación insegura permite llegar a root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000 <IP>
```

- SSH, Nginx/PHP y Gitea en el puerto 3000.
- `microblog.htb` y `app.microblog.htb`; los blogs de usuario usan subdominios.
- `feroxbuster` y `ffuf` localizan `app`, `gitea` y endpoints de edición.

## Enumeración

- El repositorio Gitea expone el código de la aplicación PHP y la configuración de Nginx.
- La edición de un blog acepta una ruta que se usa para leer y escribir archivos.
- La configuración de Nginx reenvía un prefijo a `unix:/var/run/redis/redis.sock`.
- Redis guarda el estado de la cuenta y el rol que decide si se puede subir contenido.

## Foothold

Se usa la lectura arbitraria para obtener el código y la escritura para modificar el estado en Redis. Al asignar el rol `pro` a la cuenta, la aplicación crea un directorio de subida con permisos de ejecución. Se escribe un PHP mínimo y se solicita desde el navegador para ejecutar comandos como `www-data`.

```bash
curl -s "http://app.microblog.htb/edit.php?..."
redis-cli -s /var/run/redis/redis.sock
```

La clave está en encadenar una primitiva de archivos con un servicio interno que confía en el contenido almacenado; no hace falta un CVE público.

## Escalada de privilegios

La base Redis contiene contraseñas reutilizadas por `cooper`. Tras acceder por SSH, se enumera un script Python que root ejecuta y que interpola texto controlado por el usuario. Se inyecta una expresión de plantilla para leer un archivo privilegiado y completar la escalada.

```bash
sudo -l
find / -writable -type f 2>/dev/null | head
```

## Evidencia

- Repositorio Gitea con el código vulnerable.
- Petición de edición que lee y escribe fuera del directorio del blog.
- Respuesta de Redis con el rol modificado.
- Ejecución de `id` desde la webshell y acceso SSH como `cooper`.

## Lecciones aprendidas

- Un LFI con escritura suele ser suficiente para convertir un servicio interno en RCE.
- Los sockets Unix no son una frontera de seguridad si el proxy permite rutas arbitrarias.
- Revisar el código fuente ahorra tiempo frente a probar payloads a ciegas.

## Mitigaciones y detección

- Normalizar y confinar las rutas de lectura/escritura a un directorio base.
- No exponer Redis por un `proxy_pass` y exigir autenticación al socket.
- Alertar de escrituras en directorios web y de acceso a `redis.sock` desde PHP.
- Referencias: HTB Format, 0xdf y CWE-22/CWE-94.

## Referencias

- <https://www.hackthebox.com/machines/Format>
- <https://0xdf.gitlab.io/2023/09/30/htb-format.html>
- <https://cwe.mitre.org/data/definitions/22.html>
- <https://attack.mitre.org/techniques/T1190/>
