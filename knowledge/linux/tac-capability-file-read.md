---
topic: Linux — `tac` con `cap_dac_read_search` y lectura de root
tags: [linux, capabilities, cap-dac-read-search, tac, privesc, waldo]
---

# Linux — `tac` con `cap_dac_read_search` y lectura de root

[🌐 English](tac-capability-file-read.en.md) | **Español**

## Concepto

`cap_dac_read_search` permite saltar las comprobaciones de lectura y de búsqueda en directorios (DAC). Un binario como `tac` con esa capability puede leer cualquier fichero, incluido `/root/root.txt`, sin ser setuid y sin ser root. Es una escalada de lectura, no de escritura: no da shell, pero exfiltra secretos y flags.

En Waldo, `tac` y `logMonitor` tenían `cap_dac_read_search+ei`; `tac /root/root.txt` revelaba la flag.

## Cuándo aplica

- `getcap -r /` muestra capabilities en binarios inesperados.
- La capability es `cap_dac_read_search` o `cap_dac_override`.
- El binario permite leer un fichero arbitrario (`tac`, `cat`, `less`, `head`).
- El objetivo es una flag, una clave o un fichero de configuración de root.
- En Waldo, el usuario `monitor` tenía `tac` con la capability.

## Procedimiento

1. Enumerar capabilities con `getcap -r / 2>/dev/null`.
2. Identificar un binario que lea ficheros y acepte una ruta.
3. Leer el objetivo directamente.
4. Si el orden de líneas importa, aplicar `tac` dos veces.
5. Buscar otros ficheros sensibles (`/etc/shadow`, claves SSH, configuraciones).

## Comandos

```bash
getcap -r / 2>/dev/null
tac /root/root.txt
tac /root/root.txt | tac
```

```bash
# enumerar otros objetivos
tac /etc/shadow 2>/dev/null | head
tac /root/.ssh/id_rsa 2>/dev/null
```

## Variantes

- `cap_dac_override` permite además escribir y cambiar permisos.
- `cap_dac_read_search` en `tar`, `cp` o `rsync` permite copiar el fichero.
- `logMonitor` o un binario propio con la capability puede leer logs de root.
- Combinar con `LD_PRELOAD` si el binario conserva la capability y ejecuta otro programa.

## Limitaciones

- Sin `cap_dac_read_search` ni `cap_dac_override` no se lee el fichero.
- La capability debe estar en el binario, no solo en el paquete.
- Contenedores pueden eliminar la capability del bounding set.
- No concede escritura ni una shell de root.

## Mitigación

- Auditar capabilities con `getcap -r /` y eliminarlas de binarios genéricos.
- Preferir `setcap` solo en binarios que validen la ruta y el usuario.
- Aplicar `NoNewPrivs` y un bounding set mínimo en servicios.
- Monitorizar la ejecución de `tac`, `cat` o `tar` sobre `/root`.

## Detección

- `getcap` y `capsh --print` en el host.
- Ejecución de `tac` con rutas de root.
- Lecturas de `/etc/shadow` o claves SSH por usuarios no root.
- Binarios con capabilities añadidas fuera del despliegue.

## Referencias

- [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [capsh](https://man7.org/linux/man-pages/man1/capsh.1.html)
- [0xdf — Waldo](https://0xdf.gitlab.io/2018/12/15/htb-waldo.html)
- [Ficha Waldo](../../machines/linux/waldo/README.md)
