---
topic: PHP — include escribible en un cron de root
tags: [linux, php, cron, include, privesc]
---

# PHP — include escribible en un cron de root

[🌐 English](php-cron-writable-include.en.md) | **Español**

## Concepto

Un script PHP ejecutado por cron como root puede incluir un archivo de configuración o una librería que un usuario sin privilegios puede modificar. Si el contenido se interpreta como PHP, el usuario convierte un cambio de configuración en ejecución de código con los privilegios del cron.

## Cuándo aplica

- Hay un monitor, tarea de backup o panel PHP ejecutado por root.
- El script usa `include`, `require` o `eval` sobre rutas de configuración.
- Alguno de esos archivos es escribible por `www-data` o por el usuario actual.

## Procedimiento

1. Observar procesos y cron con `pspy` para localizar ejecuciones de root.
2. Leer el script principal e identificar los `include` y las rutas que usa.
3. Comprobar permisos con `find` y `ls -l`.
4. Añadir una instrucción PHP que cree una shell SUID y esperar la siguiente ejecución.

## Comandos

```bash
pspy64 -pf -i 1000
grep -RInE "include|require|eval" /opt/website-monitor
find /opt/website-monitor -writable -type f -ls
# Payload de prueba
printf "%s\n" "<?php system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash"); ?>" >> archivo.php
```

## Variantes

- Escribir una webshell en el archivo incluido si el proceso tiene un servidor web delante.
- Usar `auto_prepend_file` o una ruta de log si el include no es directo.
- Modificar una librería de Composer o un archivo de configuración cargado por el script.

## Limitaciones

- El cron puede ejecutarse cada varios minutos; hay que esperar.
- `disable_functions` o un `open_basedir` estricto pueden bloquear la shell.
- Si el archivo se reemplaza o se valida por hash, el cambio no persiste.

## Mitigación

- Montar el monitor y sus includes como solo lectura.
- Ejecutar el cron con un usuario sin privilegios y revisar la cadena de confianza.
- Aplicar `open_basedir`, `disable_functions` y alertas de integridad.

## Detección

- Cambios en archivos PHP de configuración fuera de despliegues.
- Procesos `php` hijos de `cron` que crean archivos SUID o lanzan shells.
- Accesos de escritura de `www-data` a directorios de sistema.

## Referencias

- [0xdf — Alert](https://0xdf.gitlab.io/2025/03/22/htb-alert.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
- [PHP — include](https://www.php.net/manual/en/function.include.php)
