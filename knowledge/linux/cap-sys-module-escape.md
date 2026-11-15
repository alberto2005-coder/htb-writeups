---
topic: Linux — escape de contenedor con CAP_SYS_MODULE
tags: [linux, docker, capabilities, kernel-module, container-escape]
---

# Linux — escape de contenedor con CAP_SYS_MODULE

[🌐 English](cap-sys-module-escape.en.md) | **Español**

## Concepto

`CAP_SYS_MODULE` permite cargar y descargar módulos del kernel. Un contenedor con esta capability no está aislado del host: puede compilar o copiar un módulo que ejecute código en modo kernel y obtener control total. Es más potente que muchas configuraciones de `--privileged`.

## Cuándo aplica

- `capsh --print` muestra `cap_sys_module`.
- El contenedor comparte el kernel del host y puede escribir en `/lib/modules`.
- Se busca un escape de contenedor a root del host.

## Procedimiento

1. Enumerar capabilities y versión del kernel.
2. Compilar un módulo que ejecute un comando o abra una shell.
3. Copiarlo al contenedor y cargarlo con `insmod`.
4. Verificar la ejecución en el contexto del host.

## Comandos

```bash
capsh --print
uname -r
# Compilar un módulo mínimo en un host compatible
make -C /lib/modules/$(uname -r)/build M=$PWD modules
insmod ./escape.ko
# Alternativa: mover el módulo al contenedor y cargarlo desde allí
```

## Variantes

- Usar un módulo que modifique `modprobe_path`.
- Cargar un rootkit que oculte procesos y archivos.
- Combinar con `CAP_SYS_ADMIN` para montar el host.

## Limitaciones

- El contenedor debe compartir el kernel y permitir `init_module`.
- Secure Boot o firmas de módulos pueden bloquear la carga.
- La versión del kernel debe coincidir con las headers disponibles.

## Mitigación

- Eliminar `CAP_SYS_MODULE` de todos los contenedores.
- Aplicar seccomp y AppArmor; usar user namespaces.
- Firmar módulos y habilitar Secure Boot.

## Detección

- Llamadas a `init_module` o `finit_module` desde contenedores.
- Módulos nuevos en `/proc/modules`.
- Compiladores y headers de kernel en imágenes de producción.

## Referencias

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Docker — Runtime privileges](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [0xdf — MagicGardens](https://0xdf.gitlab.io/2025/02/08/htb-magicgardens.html)
