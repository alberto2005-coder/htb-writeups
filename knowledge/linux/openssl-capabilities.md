---
topic: OpenSSL — binario con capabilities
tags: [linux, openssl, capabilities, cap-setuid, privesc]
---

# OpenSSL — binario con capabilities

[🌐 English](openssl-capabilities.en.md) | **Español**

## Concepto

Una copia de OpenSSL con capabilities conserva privilegios aunque no sea SUID. Si tiene `cap_setuid` o `cap_setgid`, se puede cargar un motor o una biblioteca que llame a `setuid(0)` y ejecute una shell. La copia suele existir para que un servicio no root use puertos o claves, pero abre una vía directa a root.

## Cuándo aplica

- `getcap -r /` muestra una copia de OpenSSL con capabilities.
- El binario acepta `-engine` o variables de entorno como `OPENSSL_CONF`.
- El usuario puede leer o ejecutar la copia.

## Procedimiento

1. Enumerar capabilities y localizar la copia.
2. Revisar versión y opciones de carga de motores.
3. Compilar una biblioteca que llame a `setuid(0)` y `execve`.
4. Ejecutar OpenSSL con la biblioteca y obtener root.

## Comandos

```bash
getcap -r / 2>/dev/null
/usr/local/bin/openssl version
/usr/local/bin/openssl engine -t -c
gcc -shared -fPIC -o evil.so evil.c
/usr/local/bin/openssl req -engine ./evil.so -new -keyout /dev/null
```

## Variantes

- Usar `OPENSSL_CONF` para cargar un motor desde una ruta controlada.
- Aprovechar `cap_dac_read_search` para leer claves.
- Copiar el binario y mantener las capabilities si el sistema lo permite.

## Limitaciones

- La capability debe incluir `cap_setuid`.
- OpenSSL puede no cargar motores por configuración.
- El sistema puede bloquear `execve` desde el motor.

## Mitigación

- Eliminar capabilities de copias de utilidades.
- Usar `AmbientCapabilities` solo en servicios concretos.
- Auditar `getcap -r /` periódicamente.

## Detección

- Binarios con capabilities fuera de rutas estándar.
- OpenSSL cargando motores desde directorios de usuario.
- Procesos con UID 0 lanzados por un servicio.

## Referencias

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [0xdf — Lightweight](https://0xdf.gitlab.io/2019/05/11/htb-lightweight.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
