---
machine: Monitors
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, wordpress, lfi, cacti, cve-2020-14295, docker, ofbiz, cve-2020-9496, kernel-module, privesc]
---

# Monitors — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress ejecuta el plugin `wp-with-spritz`, vulnerable a inclusión de archivos. La LFI lee `wp-config.php` y obtiene la contraseña de la base de datos, que se reutiliza en el panel de Cacti de `cacti-admin.monitors.htb`. Cacti es vulnerable a la CVE-2020-14295: una SQLi en `color.php` permite actualizar `path_php_binary` y ejecutar comandos al forzar un reindexado. La shell es `www-data` en el host; el servicio de backup revela la contraseña de `marcus`. En localhost, `docker-proxy` publica en `8443` una instancia de Apache OFBiz vulnerable a la CVE-2020-9496 (deserialización Java en XML-RPC), lo que da root dentro de un contenedor privilegiado. Con `CAP_SYS_MODULE` se compila y carga un módulo del kernel que ejecuta comandos como root en el host.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: Apache con WordPress y el vhost de Cacti.

```bash
echo '<IP> monitors.htb cacti-admin.monitors.htb' | sudo tee -a /etc/hosts
wpscan --url http://monitors.htb --enumerate p
```

## Enumeración

`wpscan` detecta `wp-with-spritz`, con inclusión de archivos no autenticada en `wp.spritz.content.filter.php?url=`:

```bash
curl -s 'http://monitors.htb/wp-content/plugins/wp-with-spritz/wp.spritz.content.filter.php?url=/../../../..//etc/passwd'
```

Se lee `wp-config.php` y se obtiene la contraseña de la base de datos. Esa misma contraseña funciona en Cacti con el usuario `admin`. Cacti es vulnerable a la CVE-2020-14295.

## Foothold

La SQLi está en el parámetro `filter` de `color.php`. Permite apilar una segunda consulta que modifica la configuración:

```text
/cacti/color.php?action=export&header=false&filter=1')+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value='<CMD>'+where+name='path_php_binary';--+-
```

Después se fuerza el reindexado para ejecutar el valor:

```text
/cacti/host.php?action=reindex
```

Con un comando que devuelve una reverse shell se obtiene acceso como `www-data` en el host.

## Movimiento lateral

El servicio `cacti-backup.service` ejecuta `/home/marcus/.backup/backup.sh` como `www-data`; el script contiene la contraseña de `marcus`:

```bash
cat /etc/systemd/system/cacti-backup.service
cat /home/marcus/.backup/backup.sh
su marcus
```

Ya como `marcus`, `ps` muestra un `docker-proxy` que publica `127.0.0.1:8443` hacia otro contenedor. Se accede a él con un túnel y se identifica Apache OFBiz. La versión es vulnerable a la CVE-2020-9496, una deserialización Java no autenticada en `/webtools/control/xmlrpc`.

Se genera un payload con `ysoserial` (`CommonsBeanutils1`) que descarga y ejecuta un script, se codifica en base64 y se envía dentro del XML-RPC. La ejecución ocurre como root en el contenedor de OFBiz.

## Escalada de privilegios

El contenedor es privilegiado y tiene `CAP_SYS_MODULE`. Se compila un módulo del kernel con los headers del host y se carga con `insmod`; el módulo lanza una reverse shell o crea una bash SUID y, al ejecutarse en el contexto del host, da root fuera del contenedor.

## Evidencia

- LFI del plugin y `wp-config.php` con la contraseña de la base de datos.
- Acceso a Cacti con credenciales reutilizadas.
- SQLi en `color.php`, `path_php_binary` modificado y RCE al reindexar.
- OFBiz en `127.0.0.1:8443` y CVE-2020-9496 con `ysoserial`.
- Contenedor privilegiado, módulo del kernel cargado y root en el host.

## Lecciones aprendidas

- Un plugin abandonado puede exponer toda la instalación.
- La reutilización de contraseñas conecta WordPress y Cacti.
- Una SQLi con capacidad de escritura en `settings` se convierte en RCE.
- Los servicios internos en contenedores también son objetivos.
- `CAP_SYS_MODULE` en un contenedor privilegiado permite escapar al host.
- Los módulos del kernel se ejecutan con los privilegios máximos.

## Mitigaciones y detección

- Retirar plugins sin mantenimiento y actualizar WordPress y Cacti.
- Parametrizar consultas y restringir permisos de escritura en tablas de configuración.
- No reutilizar contraseñas entre aplicaciones.
- Segmentar servicios internos y no publicarlos sin autenticación.
- Evitar contenedores privilegiados y eliminar `CAP_SYS_MODULE`.
- Monitorizar `insmod`, `init_module` y módulos fuera del conjunto esperado.

## Referencias

- [0xdf — Monitors](https://0xdf.gitlab.io/2021/10/09/htb-monitors.html)
- [Hack The Box — Monitors](https://app.hackthebox.com/machines/monitors)
- [NVD — CVE-2020-14295](https://nvd.nist.gov/vuln/detail/CVE-2020-14295)
- [NVD — CVE-2020-9496](https://nvd.nist.gov/vuln/detail/CVE-2020-9496)
- [Knowledge — Escape con CAP_SYS_MODULE](../../../knowledge/linux/cap-sys-module-escape.md)
