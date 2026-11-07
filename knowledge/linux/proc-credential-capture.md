---
topic: proc
platform: Linux
tags: [linux, credentials, proc, race-condition]
---

# Captura de credenciales en `/proc`

[🇬🇧 English](proc-credential-capture.en.md) | **Español**

> Nota reutilizable. Pensada para scripts que se invocan con contraseñas en la línea de comandos o que las pasan por variables de entorno.

## Por qué funciona

Los argumentos de un proceso (`/proc/<pid>/cmdline`) y su entorno (`/proc/<pid>/environ`) son legibles por su propietario y por root. Si un script de mantenimiento hace `mysql -u app -p'Secreta123'` o `curl -H "Authorization: Bearer ..."`, la credencial está ahí mientras el proceso vive. En un timer, ese "mientras" son milisegundos: se trata de una **carrera**.

## Ver lo fácil

```bash
tr '\0' ' ' < /proc/self/cmdline; echo
cat /proc/self/environ | tr '\0' '\n'
ps -eo pid,user,args --sort=start_time | tail -20
```

## Capturar un proceso efímero

Bucle agresivo (suficiente cuando el timer corre cada minuto):

```bash
while true; do
  for p in /proc/[0-9]*; do
    c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null)
    case "$c" in
      *mysql*|*psql*|*redis-cli*|*curl*|*ssh*) echo "$(date +%T) ${p#/proc/}: $c" ;;
    esac
  done
done | tee /tmp/captura.log
```

Variantes:

```bash
# sólo la contraseña, cuando el patrón es conocido
watch -n 0.2 "ps -eo args | grep -oP '(?<=-p)[^ ]+' | sort -u"

# con pspy (cron/timers sin necesitar root)
./pspy64 -pf -i 100
```

Herramientas que ya hacen esto bien: `pspy`, `procmon` para Linux (eBPF) y, si hay root, `auditd` con una regla sobre `execve`.

## Qué buscar

- Contraseñas en `-p`, `--password`, `-u user:pass` (Mongo), tokens en `-H "Authorization:"`.
- `environ` con `DB_PASS`, `API_KEY`, `AWS_*`.
- Descriptores abiertos: `ls -l /proc/<pid>/fd` puede mostrar ficheros con credenciales.
- El propio script (`cat /proc/<pid>/cmdline` da la ruta): léelo si puedes.

## Convertirlo en acceso

```bash
mysql -h 127.0.0.1 -u app -p'<PASS>'
ssh <user>@<host>          # reutilización
su <user>                  # si es una cuenta local
```

## Mitigación

- Nunca pasar secretos por `argv`: usar variables de entorno leídas por el proceso, `--defaults-extra-file` (MySQL), `.pgpass`, `~/.my.cnf` con permisos 600, o un gestor de secretos.
- `hidepid=2` en `/proc` (`mount -o remount,hidepid=2 /proc`) para que cada usuario sólo vea sus procesos.
- Credenciales de un solo uso y rotación.

## Detección

- Procesos que leen `/proc/*/cmdline` de forma repetida (`pspy` al revés: un bucle en el host).
- Picos de CPU con lecturas constantes de `/proc` y procesos nuevos sin binario en disco.

## Referencias

- <https://man7.org/linux/man-pages/man5/proc.5.html>
- <https://github.com/DominicBreuker/pspy>
