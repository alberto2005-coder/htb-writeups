---
topic: safeapache2ctl — bypass de wrapper privilegiado
tags: [linux, apache, wrapper, loadmodule, include, privesc]
---

# safeapache2ctl — bypass de wrapper privilegiado

[🇬🇧 English](safeapache2ctl-bypass.en.md) | **Español**

## Concepto

Un wrapper como `safeapache2ctl` valida la configuración antes de lanzar Apache como root. Si acepta un `-f` con una configuración que el usuario controla, el `Include` permite leer archivos de root y `LoadModule` permite cargar un `.so` propio antes de que Apache falle, lo que deja ejecución privilegiada.

## Cuándo aplica

- Un script o binario privilegiado llama a `apache2ctl`.
- El wrapper valida solo la sintaxis o una ruta concreta.
- El usuario puede pasar `-f` con su propia configuración.
- `Include` o `LoadModule` se procesan antes de la comprobación final.

## Procedimiento

1. Leer el wrapper y localizar la comprobación.
2. Comprobar si acepta `-f` y si ejecuta `Include`/`LoadModule` como root.
3. Incluir un archivo de root para leer su primera línea o cargar un `.so`.
4. Ejecutar el wrapper y usar el binario SUID creado por el módulo.

```bash
printf 'Include /root/root.txt\n' > /home/<USER>/confs/x.conf
safeapache2ctl -f /home/<USER>/confs/x.conf
```

```bash
printf 'LoadModule evil /home/<USER>/confs/evil.so\n' > /home/<USER>/confs/x.conf
safeapache2ctl -f /home/<USER>/confs/x.conf
/tmp/0xdf -p
```

## Variantes

- `Include` para leer la primera línea de un archivo de root.
- `LoadModule` con un `.so` que crea un binario SUID.
- `ErrorLog`/`CustomLog` para escribir en rutas privilegiadas.
- `LD_PRELOAD` o `PATH` si el wrapper no limpia el entorno.

## Limitaciones

- El wrapper puede limpiar el entorno.
- El binario puede ser estático o usar rutas absolutas.
- AppArmor/SELinux puede bloquear la escritura.

## Mitigación

- Usar rutas absolutas y limpiar el entorno.
- Validar también los módulos y los includes.
- Ejecutar Apache con un usuario sin privilegios.

## Detección

- Configuraciones `-f` en directorios de usuario.
- `Include` de archivos fuera del webroot o de `/etc/apache2`.
- Módulos `.so` fuera de `/usr/lib/apache2` y binarios SUID nuevos.

## Referencias

- [Apache — security tips](https://httpd.apache.org/docs/2.4/misc/security_tips.html)
- [0xdf — Guardian](https://0xdf.gitlab.io/2026/02/28/htb-guardian.html)
- [CWE-426 — Untrusted Search Path](https://cwe.mitre.org/data/definitions/426.html)
