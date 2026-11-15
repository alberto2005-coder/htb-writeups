---
topic: Contenedores — escape por cwd compartido
tags: [linux, docker, container, jail-escape, cwd]
---

# Contenedores — escape por cwd compartido

[🌐 English](container-jail-cwd-escape.en.md) | **Español**

## Concepto

Un contenedor con `chroot` pero sin aislamiento de procesos puede exponer `/proc/self/cwd` como symlink al directorio del host. Si el `cwd` apunta fuera de la jaula, se pueden leer archivos del host sin privilegios de root.

## Cuándo aplica

- El contenedor comparte el filesystem o el espacio de procesos.
- `/proc` está montado y `cwd` apunta a un path del host.
- Se puede ejecutar comandos dentro del contenedor.

## Procedimiento

1. Listar `/proc/self/cwd` y sus enlaces.
2. Leer rutas relativas desde el `cwd` del host.
3. Buscar claves SSH, configuración o secretos.
4. Usar la clave para entrar al host.

## Comandos

```bash
ls -l /proc/self/cwd
cat /proc/self/cwd/../../home/jack/.ssh/id_rsa
find /proc/self/cwd -maxdepth 3 -name '*.key' 2>/dev/null
```

## Variantes

- `/proc/1/root` para escapar de la jaula.
- `/proc/self/mountinfo` para mapear el host.
- Combinar con un proceso root del host.

## Limitaciones

- PID namespace aislado oculta `/proc` del host.
- El `cwd` puede estar dentro del contenedor.
- Montajes `hidepid` limitan la lectura.

## Mitigación

- Aislar con namespaces y `pivot_root`.
- No compartir el filesystem del host.
- Ejecutar contenedores rootless y con seccomp.

## Detección

- Lecturas de `/proc/*/cwd` o `/proc/1/root`.
- Acceso a claves SSH desde un contenedor.
- Procesos del contenedor leyendo rutas del host.

## Referencias

- [0xdf — RainyDay](https://0xdf.gitlab.io/2023/02/18/htb-rainyday.html)
- [Docker — security](https://docs.docker.com/engine/security/)
- [HackTricks — container escape](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/index.html)
