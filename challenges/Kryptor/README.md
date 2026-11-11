---
challenge: Kryptor
category: Challenge
type: pwn
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [pwn, kernel, dirtypipe, cve-2022-0847, modprobe, busybox, kaslr]
---

# Kryptor — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired por evidencia de writeups públicos; no comprobado con sesión en HTB.
> Sin flags, sin offsets de la instancia y sin el binario del reto.

## TL;DR

Reto de explotación de kernel sobre **Linux 5.9.10** con SMEP, SMAP, KASLR, KPTI y `oops=panic`. El módulo `kryptor.ko` tiene una carrera real (un mutex inicializado que nunca se bloquea), pero todas las cadenas UAF chocan con `SLAB_FREELIST_HARDENED`, `HARDENED_USERCOPY`, `STRICT_MODULE_RWX` y `kptr_restrict`. El camino que funciona es **DirtyPipe (CVE-2022-0847)**: sobrescribir en la page cache la entry point de busybox y disparar `modprobe` para que el kernel lo ejecute como root.

## Enunciado y superficie

- Categoría **Pwn**, dificultad **Insane**, arranque por consola serie con QEMU.
- Entrega `bzImage`, `initramfs.cpio.gz`, `run.sh` y `kryptor.ko` (sin `strip`).
- El objetivo es leer un fichero de `/root` cuyo nombre es un SHA-256 aleatorio, con permisos `0400`.

```bash
file bzImage kryptor.ko
strings bzImage | grep -m1 "Linux version"
```

```text
Linux version 5.9.10 (x86_64)
```

Ese detalle decide todo: 5.9.10 es anterior a los kernels corregidos de DirtyPipe.

## Reconocimiento

El `init` monta `/proc`, `/sys` y `/dev`, crea el fichero de flag, carga el módulo y lanza un shell como uid 1000 (`johnny`):

```sh
FLAG=$(head -n 100 /dev/urandom | sha256sum | awk '{printf $1}')
mv /root/temp /root/$FLAG
chmod 0400 /root/$FLAG
insmod /kryptor.ko
chmod 666 /dev/kryptor
setsid cttyhack setuidgid 1000 /bin/sh
```

- `/dev/kryptor` es accesible por cualquier usuario.
- `oops=panic`: cualquier fallo del kernel reinicia la VM, sin segundas oportunidades.
- Dos CPU permiten carreras reales entre hilos.

## Análisis del módulo

`kryptor_ioctl` copia una petición de `0x18` bytes (`index`, `data_ptr`, `auth_ptr`), valida un SHA-256 contra un token embebido y despacha tres comandos:

| Comando | Operación |
|---|---|
| `0xEEEEEEEE` | reserva en `kmalloc-256`, copia `0x100` bytes y cifra con XOR |
| `0xDDDDDDDD` | descifra in-place, copia al usuario y vuelve a cifrar |
| `0xFFFFFFFF` | `kfree` y puntero a NULL |

Dos defectos destacan:

- `init_kryptor` inicializa `kryptor_lock`, pero `kryptor_ioctl` **nunca** llama a `mutex_lock` ni `mutex_unlock`.
- `n_allocations` se incrementa en ENCRYPT y no se decrementa en DELETE: el módulo admite cuatro reservas en total.

Con `userfaultfd` se puede detener `copy_from_user` a mitad de ENCRYPT y correr DECRYPT o DELETE sobre el mismo índice: UAF de lectura y escritura, y doble free.

## Por qué el UAF no basta

Cada intento de convertir la carrera en root choca con una mitigación distinta:

| Mitigación | Efecto |
|---|---|
| `CONFIG_SLAB_FREELIST_HARDENED` | punteros de freelist ofuscados con XOR; un puntero crudo se decodifica como no canónico |
| `CONFIG_HARDENED_USERCOPY` | `copy_to_user` comprueba el tamaño del objeto; leer más allá de 256 bytes aborta |
| `CONFIG_STRICT_MODULE_RWX` | `.data`/`.bss` del módulo quedan de solo lectura tras init |
| `kptr_restrict` | `/proc/kallsyms` muestra ceros para uid 1000; sin fuga de KASLR por procfs |
| `oops=panic` | un fallo de página en kernel reinicia la máquina |

La conclusión práctica: el módulo es una distracción defendida; el fallo explotable está en el kernel.

## DirtyPipe (CVE-2022-0847)

El bug está en el subsistema de pipes: al hacer `splice()` de una página de fichero a un pipe, el flag `PIPE_BUF_FLAG_CAN_MERGE` no se limpia. Un `write()` posterior cree que escribe en un hueco del pipe y escribe **directamente en la page cache** del fichero, aunque el descriptor sea de solo lectura.

Secuencia:

1. Llenar el pipe hasta su capacidad para marcar todos los buffers con `CAN_MERGE`.
2. Vaciar el pipe: los buffers se liberan, pero el flag queda.
3. `splice()` de 1 byte del fichero objetivo en `offset - 1`.
4. `write()` del payload: cae en la page cache a partir de `offset`.

Límites: no se puede escribir el byte 0 de una página, no se puede agrandar el fichero y el cambio persiste hasta que la página se expulsa.

## Explicación del fallo y cadena

El sistema es busybox y `/sbin/modprobe` es un symlink a `/bin/busybox`. La entry point del ELF está en `0x402070` y la base de carga es `0x400000`:

```text
offset en fichero = 0x402070 - 0x400000 = 0x2070
```

`0x2070` no cae en el primer byte de una página (`0x2070 % 0x1000 = 0x70`), así que DirtyPipe puede escribir ahí. El plan:

1. Sobrescribir la entry de `/bin/busybox` con shellcode posicional (unos 310 bytes).
2. Crear un fichero con magic bytes **no imprimibles** (`\xff\xff\xff\xff`) y ejecutarlo.
3. El kernel no encuentra un `binfmt`, llama a `request_module("binfmt-ffff")` y ejecuta `/sbin/modprobe` como root.
4. `modprobe` resuelve a busybox; el kernel lo carga desde la page cache corrupta y ejecuta el shellcode con uid 0.
5. El shellcode enumera `/root` con `getdents64`, lee el fichero de flag y lo copia a `/home/johnny/flag`.
6. El exploit, todavía como uid 1000, lee ese fichero.

### Tres trampas

- **Magic bytes imprimibles**: si los cuatro primeros bytes están en `0x20–0x7e`, `search_binary_handler()` asume texto y no llama a `request_module()`. Falla en silencio, sin log.
- **`modprobe` con stdout a `/dev/null`**: el shellcode no puede imprimir la flag; tiene que escribirla en un fichero.
- **Busybox corrupto para todos**: el shellcode no puede usar `system()` ni `execve("/bin/sh")`, porque `/bin/sh` también es busybox y volvería a entrar en el código corrupto. Hay que usar syscalls directas.

## Reproducción local

```bash
./run.sh
# dentro de la VM, como johnny
cat /proc/sys/kernel/modprobe      # /sbin/modprobe
readelf -h /bin/busybox | grep Entry
```

El `readelf` debe dar `0x402070`; si el binario cambia, el offset se recalcula con la misma resta.

## Explotación

```c
/* Resumen de la primitiva, no el exploit completo */
int fd = open("/bin/busybox", O_RDONLY);
int p[2]; pipe(p);
/* llenar y vaciar el pipe para dejar CAN_MERGE */
splice(fd, &off_minus_1, p[1], NULL, 1, 0);
write(p[1], shellcode, sizeof(shellcode));   /* cae en la page cache */
```

- Compilar estático con `musl-gcc` si el rootfs no trae glibc.
- Subir el binario por la consola serie (base64) y ejecutarlo como `johnny`.
- El shellcode debe abrir `/root` con `O_RDONLY|O_DIRECTORY` (`0x10000`), no `O_RDWR`.
- Los nombres de `/root` son aleatorios: se enumeran, no se adivinan.

## Evidencia

- `uname -r` o `strings bzImage` con `5.9.10`.
- Arranque con SMEP, SMAP, KASLR y KPTI (`checksec` solo cubre el binario de usuario).
- Salida del exploit con `FLAG_START`/`FLAG_END` y el contenido leído, nunca la flag real.

## Lecciones aprendidas

- Un módulo vulnerable no siempre es el camino: las mitigaciones del heap pueden cerrarlo y el kernel sigue siendo atacable por otra vía.
- DirtyPipe es un ataque de datos: no toca el heap ni necesita KASLR, por eso sobrevive a todas las protecciones de SLUB.
- La entry de un binario estático sin PIE es un objetivo estable; el offset se calcula, no se copia.
- Los detalles que no dan error son los peores: magic imprimible, stdout a `/dev/null`, busybox recursivo.
- `oops=panic` cambia la metodología: cada intento debe probarse en local antes de tocar remoto.

## Mitigaciones y detección

- Actualizar a 5.16.11, 5.15.25, 5.10.102 o posterior; en 5.9 no hay parche de esa rama.
- No confiar en KASLR para este fallo: no requiere direcciones del kernel.
- Monitorizar `modprobe_path` y ejecuciones de `/sbin/modprobe` inesperadas; verificar la integridad de binarios estáticos en la page cache.
- Alertar de `splice` sobre ficheros de solo lectura seguido de `write` al mismo pipe y de ejecuciones de ficheros con magic no imprimible.
- Referencias: CVE-2022-0847, CWE-665, MITRE T1068 y T1547.006.

## Referencias

- <https://www.echo8134.dev/w/054ee84a91fe02bb>
- <https://dirtypipe.cm4all.com/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0847>
- <https://www.cisa.gov/news-events/alerts/2022/03/10/dirty-pipe-privilege-escalation-vulnerability-linux>
