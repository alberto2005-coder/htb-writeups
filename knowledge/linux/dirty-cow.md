---
topic: Dirty COW — escritura en memoria de solo lectura (CVE-2016-5195)
tags: [linux, kernel, dirty-cow, cve-2016-5195, privesc, popcorn]
---

# Dirty COW — escritura en memoria de solo lectura (CVE-2016-5195)

[🌐 English](dirty-cow.en.md) | **Español**

## Concepto

Dirty COW es una condición de carrera en el manejo de copy-on-write del kernel Linux. Permite escribir en una página mapeada como solo lectura, incluso en un fichero que el usuario no puede modificar. El uso clásico es sobrescribir `/etc/passwd` para añadir un usuario root sin contraseña o cambiar la contraseña de root, y también se ha usado para modificar binarios setuid en memoria.

Afecta a kernels desde 2.6.22 hasta 4.8.3 (con backports en distribuciones).

## Cuándo aplica

- Kernel vulnerable y sin el parche de la distribución.
- Un binario o fichero de sistema legible y mapeable.
- Compilador disponible o un exploit precompilado para la arquitectura.
- En Popcorn se planteó como alternativa a la escalada por PAM.

## Procedimiento

1. Confirmar la versión del kernel (`uname -a`).
2. Verificar que el exploit compila para esa arquitectura.
3. Ejecutar el exploit de `/etc/passwd` o el de binario setuid.
4. Autenticarse con el usuario creado o ejecutar el binario modificado.
5. Restaurar el fichero original si se modificó.

## Comandos

```bash
uname -a
gcc -pthread dirty.c -o dirty -lcrypt
./dirty <PASSWORD>
su firefart
```

Variante para un binario setuid:

```bash
gcc -pthread cow.c -o cow
./cow /usr/bin/sudo
```

## Variantes

- `dirtycow` de firefart: crea `firefart` con UID 0 en `/etc/passwd`.
- `dirtyc0w`: escribe en un fichero de solo lectura para cambiar su contenido.
- Modificar un binario setuid para que ejecute una shell.
- Usar `ptrace` o `/proc/self/mem` en lugar de `mmap`.

## Limitaciones

- El kernel debe ser vulnerable; los parches de distribución suelen estar aplicados.
- La carrera puede fallar y requiere reintentos.
- Algunas configuraciones (SELinux, read-only root) bloquean el objetivo.
- Modificar `/etc/passwd` es ruidoso y puede romper el sistema.

## Mitigación

- Actualizar el kernel a 4.8.3 o superior, o al parche de la distribución.
- Aplicar control de integridad (AIDE, IMA) sobre `/etc/passwd` y binarios setuid.
- Ejecutar contenedores con usuario no root y root filesystem de solo lectura.
- Monitorizar escrituras en ficheros de sistema.

## Detección

- Cambios inesperados en `/etc/passwd`, `/etc/shadow` o binarios setuid.
- Procesos que mapean ficheros de sistema y escriben en `/proc/self/mem`.
- Nuevos usuarios con UID 0.
- Compilación de exploits en `/tmp` y ejecución repetida.

## Referencias

- [NVD — CVE-2016-5195](https://nvd.nist.gov/vuln/detail/CVE-2016-5195)
- [Dirty COW — dirtycow.ninja](https://dirtycow.ninja/)
- [0xdf — Popcorn](https://0xdf.gitlab.io/2018/04/21/htb-popcorn.html)
- [Ficha Popcorn](../../machines/linux/popcorn/README.md)
