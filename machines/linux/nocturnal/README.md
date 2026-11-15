---
machine: Nocturnal
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, idor, command-injection, ispconfig, sqlite]
---

# Nocturnal — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`view.php` sirve archivos por nombre sin comprobar la propiedad y permite descargar el backup de otro usuario. El panel de administración ejecuta un backup con un parámetro controlable; los saltos de línea y tabulaciones saltan el filtro y dan una shell. La base SQLite contiene el hash MD5 de `tobias`, y el panel de ISPConfig es vulnerable a CVE-2023-46818, lo que lleva a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04 y `80/tcp` nginx con `nocturnal.htb`.
- La web permite registrarse, subir archivos y verlos con `view.php?filename=`.
- `admin.nocturnal.htb` aloja un panel de administración con login.

## Enumeración

- `view.php` no valida el propietario: se pueden pedir archivos de otros usuarios.
- Los backups se guardan como `<user>_<timestamp>.zip` y se descargan desde la misma ruta.
- El backup del administrador contiene la base SQLite con usuarios y hashes MD5.

## Foothold

Se descarga el backup ajeno y se extrae la base. El hash de `tobias` se crackea y se usa para entrar al panel admin. La función de backup concatena el nombre del archivo en un comando; se inyecta con `%0a` y tabulaciones para evadir el filtro.

```bash
curl 'http://nocturnal.htb/view.php?filename=<ADMIN>_<TS>.zip' -o admin.zip
unzip admin.zip
hashcat -m 0 hash.txt rockyou.txt
# En el panel: nombre de backup con salto de línea y tab
```

## Movimiento lateral

La shell cae como `www-data`. La base y los archivos de configuración permiten pasar a `tobias` por SSH; su contraseña se reutiliza en el panel de ISPConfig.

## Escalada de privilegios

ISPConfig 3.2.11 es vulnerable a CVE-2023-46818: el parámetro `language_file` del editor de idiomas permite incluir un archivo PHP y ejecutar código como el usuario del panel, que es root.

```bash
python3 cve-2023-46818.py http://localhost:8080 <USER> <PASSWORD>
# La exploit escribe un PHP y lo invoca desde el editor de idiomas
```

## Evidencia

- Backup ajeno descargado con `view.php`.
- Hash MD5 crackeado y acceso al panel admin.
- Shell de `www-data` y ejecución como root vía ISPConfig.

## Lecciones aprendidas

- Un identificador de archivo debe validar la propiedad en el servidor.
- Los filtros de comandos basados en listas negras se evaden con saltos de línea.
- Un panel de hosting con root y un CVE reciente compromete todo el host.

## Mitigación y detección

- Usar IDs y comprobar que el recurso pertenece al usuario autenticado.
- Ejecutar backups con `execve` y argumentos separados, nunca con una shell.
- Mantener ISPConfig actualizado y limitar su acceso a la red interna.

## Referencias

- [0xdf — Nocturnal](https://0xdf.gitlab.io/2025/08/16/htb-nocturnal.html)
- [IppSec — Nocturnal](https://www.youtube.com/watch?v=tjA3sXsnPqw)
- [Hack The Box — Nocturnal](https://app.hackthebox.com/machines/nocturnal)
