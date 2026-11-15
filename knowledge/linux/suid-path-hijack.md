---
topic: SUID — secuestro de PATH y rutas relativas
tags: [linux, suid, path, privesc, backup]
---

# SUID — secuestro de PATH y rutas relativas

[🌐 English](suid-path-hijack.en.md) | **Español**

## Concepto

Un binario SUID que ejecuta otro programa sin ruta absoluta busca en `PATH`. Si el usuario puede escribir un directorio anterior en `PATH`, coloca allí un ejecutable con el mismo nombre y el binario lo lanza con privilegios de root. El fallo no está en el SUID, sino en cómo resuelve sus dependencias.

## Cuándo aplica

- `find / -perm -4000` muestra un binario no estándar.
- `strings` revela llamadas a `cat`, `tar`, `cp` o scripts sin ruta.
- El usuario controla algún directorio de `PATH`.

## Procedimiento

1. Enumerar binarios SUID y revisar su comportamiento.
2. Identificar la dependencia sin ruta absoluta.
3. Crear el ejecutable malicioso en un directorio controlado.
4. Ejecutar el SUID con `PATH` modificado.

## Comandos

```bash
find / -perm -4000 -type f 2>/dev/null
strings /usr/bin/backup | grep -iE "cat|tar|cp|sh"
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/cat && chmod +x /tmp/bin/cat
PATH=/tmp/bin:$PATH /usr/bin/backup
```

## Variantes

- Secuestrar un script invocado por `system()` o `popen()`.
- Aprovechar un directorio de trabajo relativo (`./`).
- Usar `LD_PRELOAD` si el binario lo permite.

## Limitaciones

- `PATH` puede estar limpio en el entorno del SUID.
- El binario puede usar rutas absolutas.
- Las capacidades y SELinux pueden limitar la ejecución.

## Mitigación

- Usar rutas absolutas en binarios privilegiados.
- Limpiar `PATH` y no incluir directorios de usuario.
- Auditar SUID y aplicar mínimo privilegio.

## Detección

- SUID que lanzan procesos desde directorios temporales.
- Cambios en `PATH` de procesos privilegiados.
- Binarios con nombres de utilidades en `/tmp`.

## Referencias

- [0xdf — Lazy](https://0xdf.gitlab.io/2020/07/29/htb-lazy.html)
- [GTFOBins — PATH](https://gtfobins.github.io/gtfobins/env/)
- [CWE-426 — Untrusted Search Path](https://cwe.mitre.org/data/definitions/426.html)
