---
machine: Pit
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, snmp, seeddms, cve-2019-12744, selinux, cockpit, privesc]
---

# Pit — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP con comunidad `public` filtra la ruta de SeedDMS y su versión 5.1.15. SeedDMS permite subir PHP a `data/` y ejecutarlo; CVE-2019-12744 se corrigió añadiendo un `.htaccess` que nginx ignora. La shell como `nginx` permite leer `settings.xml` y entrar por SSH como `michelle`. Un ACL en `/usr/local/monitoring` deja escribir scripts que `/usr/bin/monitor` ejecuta como root desde SNMP extend.

## Reconocimiento

```bash
nmap -Pn -sSUV -p22,80,161,9090 <IP>
snmpwalk -v2c -c public <IP>
```

- `22` OpenSSH, `80` web, `161/udp` SNMP y `9090` Cockpit.
- SNMP revela procesos, rutas y el directorio `/var/www/html/seeddms51x/seeddms`.
- La web es SeedDMS 5.1.15.

## Enumeración

Con la ruta y la versión se busca CVE-2019-12744. El fallo permite subir archivos PHP como documentos y ejecutarlos desde `data/`; el `.htaccess` del parche solo funciona en Apache, no en nginx. `settings.xml` contiene las credenciales de la base y de `michelle`.

## Foothold

Se sube un archivo PHP como documento y se accede a `/data/1048576/<id>/1.php`. La ejecución confirma la webshell. Una reverse shell directa falla por SELinux; la webshell sigue siendo suficiente.

```text
/data/1048576/<id>/1.php?cmd=id
```

## Movimiento lateral

`settings.xml` revela credenciales de SeedDMS y del sistema. La contraseña de `michelle` funciona por SSH. Cockpit en `9090` ofrece otra vía de administración.

## Escalada de privilegios

`getfacl /usr/local/monitoring` muestra que `michelle` puede escribir en el directorio. `/usr/bin/monitor` recorre los `check*.sh` y los ejecuta como root; SNMP extend lo invoca. Se escribe un script que añade una clave pública a `/root/.ssh/authorized_keys` y se dispara con `snmpwalk` sobre `NET-SNMP-EXTEND-MIB::nsExtendObjects`.

```bash
echo 'echo "<clave>" | tee /root/.ssh/authorized_keys' > check_x.sh
snmpwalk -v1 -c public <IP> NET-SNMP-EXTEND-MIB::nsExtendObjects
```

## Evidencia

- SNMP con la ruta de SeedDMS.
- Webshell en `/data/1048576/`.
- `settings.xml` con credenciales.
- Script en `monitoring` ejecutado por SNMP como root.

## Lecciones aprendidas

- SNMP con comunidad por defecto expone rutas y procesos.
- Un `.htaccess` no protege `data/` si el servidor es nginx.
- SELinux puede bloquear la reverse shell sin impedir la ejecución de comandos.
- Un ACL de escritura en un directorio de scripts ejecutados por root es root.

## Mitigación y detección

- Cambiar la comunidad SNMP y filtrar `161/udp`.
- Actualizar SeedDMS, bloquear la ejecución de PHP en `data/` y no confiar solo en `.htaccess`.
- Revisar ACLs de directorios ejecutados por root.
- Alertar sobre nuevos `check*.sh` y sobre `nsExtend` en SNMP.

## Referencias

- [0xdf — Pit](https://0xdf.gitlab.io/2021/09/25/htb-pit.html)
- [IppSec — Pit](https://www.youtube.com/watch?v=IF5uhe1qR2I)
- [Hack The Box — Pit](https://app.hackthebox.com/machines/pit)
