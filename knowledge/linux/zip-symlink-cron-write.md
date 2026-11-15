---
topic: Cron — symlink predecible y escritura arbitraria
tags: [linux, cron, symlink, arbitrary-write, privesc]
---

# Cron — symlink predecible y escritura arbitraria

[🌐 English](zip-symlink-cron-write.en.md) | **Español**

## Concepto

Un proceso root que genera nombres de archivo con `rand()` o una marca de tiempo predecible y sigue symlinks permite redirigir la escritura a un archivo sensible, como `/root/.ssh/authorized_keys`.

## Cuándo aplica

- El cron se ejecuta en un segundo o patrón conocido.
- El nombre del archivo se calcula con un PRNG predecible.
- El directorio de salida es escribible por el atacante.

## Procedimiento

1. Observar la hora exacta del cron.
2. Reproducir el cálculo del nombre.
3. Crear un symlink al archivo objetivo.
4. Insertar el contenido en la base o en la entrada.

## Comandos

```bash
ln -s /root/.ssh/authorized_keys /var/local/<HASH>
# insertar la clave pública en la tabla que lee el cron
# esperar la ejecución y entrar por SSH
```

## Variantes

- Escritura en `/etc/cron.d` o un script de backup.
- Nombres basados en `date` o en un contador.
- Carrera entre comprobación y escritura.

## Limitaciones

- El nombre puede incluir bytes aleatorios fuertes.
- El directorio puede tener `fs.protected_symlinks`.
- El proceso puede usar `O_NOFOLLOW`.

## Mitigación

- Usar `mkstemp` y `O_NOFOLLOW`.
- No ejecutar backups como root.
- Escribir en directorios no controlados por usuarios.

## Detección

- Symlinks en `/var/local` o directorios de backup.
- Claves nuevas en `authorized_keys`.
- Ejecuciones de cron que escriben fuera de su directorio.

## Referencias

- [0xdf — CrossFit](https://0xdf.gitlab.io/2021/03/20/htb-crossfit.html)
- [CWE-59 — Link Following](https://cwe.mitre.org/data/definitions/59.html)
- [Linux — protected_symlinks](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/fs.html)
