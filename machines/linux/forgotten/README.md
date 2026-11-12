---
machine: Forgotten
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, limesurvey, docker, plugin-upload, sudo]
---

# Forgotten — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

Instancia de LimeSurvey sin instalar. El asistente de instalación permite apuntar a un MySQL propio y crear una cuenta superadmin. Desde la administración se sube un plugin malicioso para obtener RCE en el contenedor. Una variable de entorno con la contraseña de LimeSurvey se reutiliza para el usuario del host, y una regla de `sudo` permite root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 22,80 -sCV <IP>
```

El puerto 80 sirve el instalador de LimeSurvey. La aplicación corre en un contenedor Debian, mientras que SSH apunta a un host Ubuntu.

```bash
curl -s http://<IP>/ | head
```

## Acceso inicial

Se levanta un MySQL accesible desde la instancia y se completa el asistente:

```bash
docker run --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=<PASSWORD> mysql:5.7
```

En el instalador se configura la base de datos, se crea el administrador y se termina la instalación. Después se sube un plugin con código PHP:

```text
plugins/ExampleSettings/ExampleSettings.php
```

El plugin se activa desde la administración y ejecuta una reverse shell:

```bash
nc -lnvp 443
```

La shell cae como `limesvc` dentro del contenedor.

## Escalada

Se revisan variables de entorno y procesos:

```bash
env
cat /proc/1/environ | tr '\0' '\n'
sudo -l
```

La contraseña de `LIMESURVEY_PASS` se reutiliza para el usuario `limesvc` del host. Se entra por SSH:

```bash
ssh limesvc@<IP>
```

En el host, `sudo -l` muestra una regla que permite ejecutar un comando como root; se abusa de ella para obtener una shell.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Un instalador sin terminar permite crear el administrador.
- La subida de plugins es ejecución de código si no hay validación.
- Las variables de entorno de contenedores suelen contener secretos reutilizados.
- Un contenedor comprometido puede dar acceso al host por reutilización.

## Detección y mitigación

- Bloquear el instalador después del despliegue y exigir autenticación.
- Validar y firmar plugins; limitar la escritura en `upload/plugins`.
- No reutilizar contraseñas entre contenedor y host; usar secretos dedicados.
- Revisar reglas `sudo` y ejecutar contenedores sin privilegios.

## Referencias

- <https://0xdf.gitlab.io/2025/09/16/htb-forgotten.html>
- <https://docs.limesurvey.org/Plugins+at+a+glance>
- <https://attack.mitre.org/techniques/T1505/003/>
