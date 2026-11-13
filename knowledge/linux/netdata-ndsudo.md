---
topic: NetData ndsudo privilege escalation
tags: [linux, netdata, ndsudo, cve-2024-32019, path-hijack, suid]
---

# NetData ndsudo privilege escalation

[🌐 English](netdata-ndsudo.en.md) | **Español**

## Concepto

El helper `ndsudo` de NetData se instala como SUID root para ejecutar utilidades de disco. En versiones afectadas resuelve el binario por `PATH` sin usar una ruta absoluta (CVE-2024-32019), por lo que un usuario del grupo `netdata` puede colocar un ejecutable con el nombre esperado y obtener root.

## Cuándo aplica

- NetData instalado fuera de un paquete actualizado.
- `ndsudo` con bit SUID.
- Usuario dentro del grupo `netdata` o con acceso al directorio del helper.
- Llamadas como `ndsudo nvme-list`.

## Procedimiento

1. Enumerar permisos y grupos del usuario.
2. Localizar `ndsudo` y confirmar SUID.
3. Revisar las cadenas y los subcomandos disponibles.
4. Crear un binario con el nombre de una utilidad esperada.
5. Ejecutar el helper con un `PATH` controlado.

```bash
find / -perm -4000 -name ndsudo 2>/dev/null
strings /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo | grep -E '^[a-z][a-z-]*$'
PATH=/tmp/p:$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
```

## Variantes

- Hijack de `nvme`, `smartctl` u otra utilidad invocada.
- Escritura de un ELF que llama a `setuid(0)` y lanza una shell.
- Abuso del grupo `netdata` para leer configuración o sockets.
- Enumeración de otros helpers SUID del mismo producto.

## Limitaciones

- El usuario debe poder escribir en un directorio del `PATH`.
- La versión corregida usa rutas absolutas.
- El binario debe conservar el bit de ejecución.
- AppArmor o SELinux pueden restringir la ejecución.

## Mitigación y detección

- Actualizar NetData y retirar el SUID de `ndsudo` si no es necesario.
- Ejecutar helpers con rutas absolutas y `PATH` saneado.
- Restringir el grupo `netdata`.
- Auditar ejecuciones de `ndsudo` y cambios de `PATH` en procesos privilegiados.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2024-32019>
- <https://github.com/netdata/netdata/security/advisories>
- <https://attack.mitre.org/techniques/T1574/007/>
