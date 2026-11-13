---
machine: Planning
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2024-9264, docker, credential-reuse, crontab-ui]
---

# Planning — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un subdominio expone Grafana 11.0.0 con credenciales de administrador. CVE-2024-9264 permite ejecutar comandos mediante SQL Expressions y DuckDB. Desde el contenedor se filtra la contraseña de un usuario del host; la reutilización permite SSH y un Crontab UI local ejecutado como root completa la escalada.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH y nginx.
- El dominio base es `planning.htb`.
- La enumeración de vhosts descubre `grafana.planning.htb`.

```bash
ffuf -u http://planning.htb -H 'Host: FUZZ.planning.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 178
```

## Enumeración

- Grafana muestra la versión 11.0.0 en el pie de la página.
- El enunciado proporciona credenciales de administrador; se usan solo en la instancia.
- La versión es anterior a la corrección de CVE-2024-9264, una inyección en SQL Expressions.

## Foothold

La consulta llega a DuckDB y permite cargar la extensión `shellfs`, que ejecuta comandos del sistema. Se envía una petición autenticada a `/api/ds/query` con una expresión que escribe un script y lo ejecuta.

```bash
curl -s -b cookies.txt -H 'Content-Type: application/json' \
  -X POST http://grafana.planning.htb/api/ds/query \
  --data @query.json
```

El comando se ejecuta como root dentro del contenedor de Grafana. Se obtiene una reverse shell y se confirma con `id`.

## Movimiento lateral

Las variables de entorno del contenedor incluyen `GF_SECURITY_ADMIN_USER=enzo` y una contraseña. Esa misma contraseña funciona para SSH en el host.

```bash
env | grep -i -E 'admin|password|secret'
ssh enzo@planning.htb
```

## Escalada de privilegios

`ps aux` y `ss -lntp` muestran un Crontab UI escuchando en `127.0.0.1:8000`. Se reenvía el puerto y se accede al panel, que se ejecuta como root.

```bash
ssh -L 8000:127.0.0.1:8000 enzo@planning.htb -N
```

Se crea una tarea programada que copia `/bin/bash` y le aplica SUID. Al ejecutarse como root, `enzo` obtiene una shell efectiva de root.

```bash
cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash
/tmp/rootbash -p
```

## Evidencia

- Respuesta de `id` en el contenedor y en el host.
- Variables de entorno con valores redactados.
- Captura de Crontab UI y de la tarea creada.
- Flag redactada.

## Lecciones aprendidas

- Una versión concreta en el pie de una aplicación sigue siendo una pista válida.
- Los secretos del entorno de un contenedor pueden reutilizarse en el host.
- Los paneles de administración ligados a `localhost` no están fuera del alcance: un túnel SSH los alcanza.

## Mitigaciones y detección

- Actualizar Grafana a una versión corregida y restringir SQL Expressions.
- No ejecutar Grafana como root ni reutilizar credenciales entre contenedor y host.
- Proteger Crontab UI con autenticación y escuchar solo en una interfaz administrativa.
- Auditar la creación de tareas cron y la aparición de binarios SUID.

## Referencias

- <https://www.hackthebox.com/machines/Planning>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-9264>
- <https://grafana.com/security/security-advisories/cve-2024-9264/>
- <https://attack.mitre.org/techniques/T1190/>
