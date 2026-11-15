---
title: Carrera de archivos temporales — leer /etc/shadow
tags: [linux, race-condition, symlink, privesc, tmp]
---

# Carrera de archivos temporales — leer /etc/shadow

[🇬🇧 English](tmp-race-shadow-read.en.md) | **Español**

## Concepto

Un script privilegiado que copia `/etc/shadow` a un archivo temporal con nombre predecible y lo borra después de autenticar permite una carrera. Si el atacante reemplaza el archivo por un symlink a un destino que puede leer, o lo abre antes de que se borre, obtiene los hashes.

## Cuándo aplica

- `sudo -l` muestra un script que copia o escribe archivos como root.
- El destino está en `/tmp`, `/dev/shm` o el directorio del usuario.
- El nombre del archivo es fijo o sigue un patrón adivinable.

## Procedimiento

1. Leer el script y localizar la creación del temporal.
2. Vigilar el directorio con `inotifywait`.
3. En cuanto aparezca, copiarlo o sustituirlo por un symlink.
4. Crackear los hashes o usar el archivo para otra escalada.

```bash
inotifywait -m -e create -e moved_to /tmp &
while true; do
  for f in /tmp/.shadow* /tmp/shadow*; do
    [ -f "$f" ] && cp "$f" /dev/shm/leak 2>/dev/null && break
  done
done
```

## Variantes

- Symlink a un archivo que el atacante controla para que el script escriba como root.
- `O_NOFOLLOW` ausente en el script permite el symlink.
- La carrera también sirve para `authorized_keys` o tareas de backup.

## Limitaciones

- El archivo puede tener permisos 600 y borrarse muy rápido.
- `fs.protected_symlinks` y `fs.protected_regular` mitigan parte del ataque.
- Se necesita acceso local y el script debe ejecutarse como root.

## Mitigación y detección

- Usar `mkstemp()` y `O_NOFOLLOW`, y borrar con `unlink` seguro.
- No copiar `/etc/shadow`; usar PAM o `getspnam`.
- Montar `/tmp` con `nosuid,nodev` y proteger symlinks.
- Auditar ejecuciones de scripts privilegiados y archivos temporales.

## Referencias

- <https://man7.org/linux/man-pages/man7/inotify.7.html>
- <https://cwe.mitre.org/data/definitions/367.html>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
