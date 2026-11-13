---
machine: PermX
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, chamilo, cve-2023-4220, file-upload, setfacl, symlink]
---

# PermX — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Chamilo LMS expone una subida sin autenticación que permite ejecutar PHP. La configuración filtra credenciales de base de datos reutilizadas por un usuario del sistema. La escalada abusa de un script `sudo` que aplica `setfacl` siguiendo un enlace simbólico.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH y HTTP.
- El dominio principal es `permx.htb`.
- La enumeración de vhosts descubre `lms.permx.htb`.

## Enumeración

- `lms.permx.htb` ejecuta Chamilo LMS 1.11.24.
- La ruta de administración y la versión son visibles en cabeceras y recursos estáticos.
- Se revisan los endpoints de subida y el código público de la versión.

## Foothold

Chamilo es vulnerable a CVE-2023-4220: una subida sin autenticación en `bigUpload.php`.

```bash
curl -s -F "bigUploadFile=@shell.php" \
  "http://lms.permx.htb/main/inc/lib/javascript/bigupload/inc/bigUpload.php?action=post-unsupported"
curl -s "http://lms.permx.htb/main/inc/lib/javascript/bigupload/files/shell.php?cmd=id"
```

El archivo queda accesible bajo `main/inc/lib/javascript/bigupload/files/`. Se obtiene ejecución como el usuario del servicio web.

## Movimiento lateral

La configuración de Chamilo contiene las credenciales de base de datos. La contraseña se reutiliza para la cuenta `mtz`.

```bash
ssh mtz@permx.htb
```

## Escalada de privilegios

`sudo -l` muestra un script que aplica ACL a archivos de un directorio concreto:

```bash
sudo -l
sudo /opt/acl.sh <USER> rwx /home/mtz/archivo
```

El script comprueba el prefijo de la ruta, pero `setfacl` sigue enlaces simbólicos. Se crea un enlace en la ruta permitida apuntando a `/etc/passwd`; al aplicar la ACL, `mtz` obtiene escritura y puede añadir un usuario root.

## Evidencia

- Respuesta de `id` desde el webshell.
- Captura de `sudo -l` y del script.
- ACL aplicada mediante enlace simbólico.
- Flag redactada.

## Lecciones aprendidas

- Una subida sin autenticación no necesita un endpoint llamativo.
- La reutilización de contraseñas convierte una filtración de configuración en acceso SSH.
- Validar el prefijo de una ruta no equivale a validar el archivo real.

## Mitigaciones y detección

- Actualizar Chamilo y eliminar la subida heredada.
- No reutilizar credenciales de servicio para cuentas humanas.
- Resolver la ruta con `realpath` y rechazar enlaces simbólicos.
- Auditar ejecuciones de `setfacl` desde `sudo` y cambios de ACL en archivos del sistema.

## Referencias

- <https://www.hackthebox.com/machines/permx>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-4220>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1548/001/>
