---
topic: Linux — mmap de memoria y sobrescritura de credenciales
tags: [linux, kernel, mmap, cred, privesc]
---

# Linux — mmap de memoria y sobrescritura de credenciales

[🇬🇧 English](mmap-cred-overwrite.en.md) | **Español**

## Concepto

Un módulo o dispositivo que permite `mmap` sobre memoria física rompe el aislamiento del kernel. Si el atacante puede mapear y escribir memoria arbitraria, puede localizar la estructura `cred` de su proceso y cambiar `uid` y `gid` a 0 sin ejecutar un binario SUID.

## Cuándo aplica

- Existe `/dev/<name>` creado por un módulo vulnerable.
- El dispositivo permite `mmap` con `PROT_WRITE` y `MAP_SHARED`.
- No hay SMEP/SMAP ni restricciones de `perf_event` o `/dev/mem`.

## Procedimiento

1. Enumerar dispositivos y módulos con `ls -l /dev`, `dmesg` y `lsmod`.
2. Abrir el dispositivo y mapear una página.
3. Buscar la estructura `cred` del proceso actual.
4. Escribir `uid=0` y `gid=0`, y comprobar con `id`.

```c
int fd = open("/dev/dhid", O_RDWR);
void *map = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
// localizar cred y sobrescribir uid/gid
```

## Variantes

- Escribir directamente en `/dev/mem` o `/dev/kmem`.
- Usar `/proc/kcore` si es legible.
- Modificar `modprobe_path` o una función del kernel.

## Limitaciones

- Requiere un dispositivo o módulo vulnerable.
- KASLR complica localizar estructuras.
- Un kernel parcheado bloquea `mmap` de memoria física.

## Mitigación

- Eliminar módulos que exponen memoria física.
- Aplicar SMEP, SMAP, KASLR y `CONFIG_STRICT_DEVMEM`.
- Restringir permisos de `/dev` y auditar módulos de terceros.

## Detección

- `mmap` de dispositivos no estándar por procesos de usuario.
- Cambios de UID sin `setuid` ni `sudo`.
- Módulos cargados fuera del inventario.

## Referencias

- [0xdf — Smasher2](https://0xdf.gitlab.io/2019/12/14/htb-smasher2.html)
- [Linux kernel — credentials](https://www.kernel.org/doc/html/latest/security/credentials.html)
- [CWE-123 — Write-what-where Condition](https://cwe.mitre.org/data/definitions/123.html)
