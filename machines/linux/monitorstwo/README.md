---
machine: MonitorsTwo
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, cacti, cve-2022-46169, docker, cve-2021-41091, suid]
---

# MonitorsTwo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Cacti 1.2.22 es vulnerable a CVE-2022-46169: el parámetro `X-Forwarded-For` permite ejecutar comandos sin autenticación. La shell cae dentro de un contenedor Docker con `capsh` SUID, lo que da root en el contenedor. Las credenciales de MySQL permiten volcar un hash y acceder por SSH a `marcus`; la versión de Docker es vulnerable a CVE-2021-41091, y un bash SUID copiado desde el contenedor escala en el host.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y Cacti sobre HTTP.
- La versión de Cacti aparece en la respuesta y en los archivos estáticos.
- El contenedor expone MySQL en la red interna.

## Enumeración

- Cacti 1.2.22 y el endpoint `remote_agent.php` son accesibles.
- La aplicación confía en `X-Forwarded-For` para autorizar la acción.
- Dentro del contenedor, `capsh` tiene el bit SUID.
- `/var/www/html/include/config.php` contiene credenciales de MySQL.

## Foothold

Se envía una petición a `remote_agent.php` con una IP permitida y un `poller_id` que inyecta un comando. La respuesta ejecuta una reverse shell como el usuario del servicio web dentro del contenedor.

```bash
curl -s "http://<IP>/remote_agent.php?action=polldata&local_data_ids[]=1"   -H 'X-Forwarded-For: 127.0.0.1'
```

## Escalada de privilegios

`/sbin/capsh` SUID permite root dentro del contenedor. Con las credenciales de MySQL se vuelca la tabla de usuarios, se crackea el hash de `marcus` y se accede por SSH al host. Docker 20.10.14 es vulnerable a CVE-2021-41091: como root del contenedor se escribe un bash SUID en el overlay y se ejecuta desde el host.

```bash
find / -perm -4000 -type f 2>/dev/null
mysql -u <USER> -p -e 'select * from user_auth'
```

## Evidencia

- Respuesta de Cacti con el comando ejecutado.
- `id` como root dentro del contenedor.
- Hash de `marcus` y sesión SSH.
- Bash SUID en el overlay y root en el host.

## Lecciones aprendidas

- Una cabecera de proxy puede ser una decisión de autorización.
- Un contenedor comprometido no contiene el impacto si el runtime es vulnerable.
- Revisar siempre la versión de Docker y los SUID del contenedor.

## Mitigaciones y detección

- Actualizar Cacti y no confiar en `X-Forwarded-For` sin un proxy validado.
- Actualizar Docker y restringir la API y los montajes.
- Monitorizar `remote_agent.php` con IPs externas y creación de SUID.
- Referencias: NVD CVE-2022-46169, CVE-2021-41091, HTB MonitorsTwo.

## Referencias

- <https://www.hackthebox.com/machines/MonitorsTwo>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-46169>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-41091>
- <https://attack.mitre.org/techniques/T1190/>
