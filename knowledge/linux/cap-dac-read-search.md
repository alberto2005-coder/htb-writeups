---
topic: Linux — CAP_DAC_READ_SEARCH en contenedores
tags: [linux, docker, capabilities, dac-read-search, container-escape]
---

# Linux — CAP_DAC_READ_SEARCH en contenedores

[🌐 English](cap-dac-read-search.en.md) | **Español**

## Concepto

`CAP_DAC_READ_SEARCH` permite ignorar los permisos de lectura de archivos y directorios. Un contenedor con esta capability y un montaje del host puede leer claves, configuraciones y sombras de contraseñas; si además hay escritura, puede modificar tareas privilegiadas y ejecutar como root.

## Cuándo aplica

- `capsh --print` muestra `cap_dac_read_search`.
- El contenedor monta directorios del host o comparte el namespace de procesos.
- Se busca leer secretos o escribir una tarea privilegiada.

## Procedimiento

1. Enumerar capabilities y montajes.
2. Leer archivos protegidos del host con la capability.
3. Buscar una ruta de escritura o una tarea que se ejecute como root.
4. Crear o modificar el archivo y esperar la ejecución.

## Comandos

```bash
capsh --print
mount | grep -E "host|docker|/root"
cat /proc/1/root/etc/shadow 2>/dev/null
# Si hay escritura, crear una tarea o clave
ls -la /proc/1/root/root/.ssh/
```

## Variantes

- Leer claves SSH y reutilizarlas fuera del contenedor.
- Modificar un cron o un script de inicio del host.
- Combinar con `CAP_DAC_OVERRIDE` para escritura.

## Limitaciones

- La capability solo afecta a lectura, no a escritura.
- El contenedor debe ver la ruta del host.
- SELinux/AppArmor pueden bloquear el acceso.

## Mitigación

- Eliminar `CAP_DAC_READ_SEARCH` de los contenedores.
- Montar secretos como solo lectura y usar user namespaces.
- Aplicar seccomp/AppArmor y revisar capabilities.

## Detección

- Contenedores que leen `/etc/shadow` o claves del host.
- Uso de `CAP_DAC_READ_SEARCH` en procesos noroot.
- Accesos a `/proc/1/root` desde contenedores.

## Referencias

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Docker — Runtime privileges](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [0xdf — Talkative](https://0xdf.gitlab.io/2022/08/27/htb-talkative.html)
