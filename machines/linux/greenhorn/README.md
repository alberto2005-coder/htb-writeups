---
machine: GreenHorn
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, pluck-cms, gitea, webshell, depix, credential-recovery]
---

# GreenHorn — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un Gitea expuesto filtra la configuración y la contraseña de administración de Pluck CMS. Con acceso al panel se sube un módulo PHP y se obtiene ejecución. La base de Gitea permite recuperar otra cuenta; un PDF con una contraseña pixelada lleva a root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80,3000 <IP>
```

- SSH, HTTP y Gitea en 3000.
- Vhosts: `greenhorn.htb` y `git.greenhorn.htb`.

## Enumeración

- El sitio principal usa Pluck CMS 4.7.18.
- Gitea aloja un repositorio público con la configuración del sitio.
- El repositorio expone credenciales o un hash del panel de Pluck.
- Se identifica el panel `/admin.php`.

## Foothold

Con la cuenta de administración se sube un módulo malicioso. Pluck permite instalar módulos como archivos PHP y ejecutarlos desde el directorio de módulos.

```bash
# Empaquetar un módulo con el PHP de ejecución y subirlo desde el panel
curl -s -b cookies.txt "http://greenhorn.htb/admin.php?action=installmodule"
```

El módulo devuelve ejecución como `www-data`.

## Movimiento lateral

La base `gitea.db` contiene hashes de las cuentas de Gitea. Se extrae el hash del usuario `git` y se crackea fuera de la máquina.

```bash
sqlite3 gitea.db "select name,passwd_hash_algo,passwd from user;"
ssh git@greenhorn.htb
```

## Escalada de privilegios

En el home de `git` hay un PDF con la contraseña de root pixelada. La imagen se procesa con Depix para recuperar los caracteres.

```bash
python3 depix.py -p blurred.png -s search_image.png -o recovered.png
su root
```

## Evidencia

- Repositorio y archivo de configuración expuestos.
- Módulo PHP y salida de `id`.
- Hash de Gitea y acceso SSH.
- PDF y contraseña recuperada, redactados.

## Lecciones aprendidas

- Un repositorio público puede filtrar secretos aunque el sitio principal parezca pequeño.
- Los módulos de un CMS son código ejecutable.
- La pixelación no es una protección criptográfica de una credencial.

## Mitigaciones y detección

- No publicar configuraciones ni credenciales en repositorios.
- Restringir la instalación de módulos y validar su contenido.
- Rotar credenciales y usar un gestor de secretos.
- Monitorizar subidas a directorios de módulos y accesos anómalos a `gitea.db`.

## Referencias

- <https://www.hackthebox.com/machines/greenhorn>
- <https://github.com/spipm/Depix>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://attack.mitre.org/techniques/T1552/>
