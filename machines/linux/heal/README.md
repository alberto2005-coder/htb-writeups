---
machine: Heal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, rails, lfi, limesurvey, consul, privesc]
---

# Heal — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web usa tres dominios: principal, API y encuestas. La API tiene un directory traversal en `/download` que permite leer la configuración de Rails y las bases SQLite; el hash del admin se crackea y se reutiliza en LimeSurvey. Un plugin PHP da un webshell como `www-data`; la contraseña de PostgreSQL se reutiliza para `ron`, y un Consul sin autenticación en localhost permite registrar un servicio que ejecuta un check como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` nginx con una web de generación de currículums.
- Vhosts `heal.htb`, `api.heal.htb` y `take-survey.heal.htb`.
- La API emite JWT y el sitio de encuestas es LimeSurvey 6.6.4.

## Enumeración

Se registra una cuenta y se obtiene un JWT. `/download?filename=` devuelve archivos sin normalizar la ruta; con `../../` se leen `config/database.yml`, `storage/development.sqlite3` y `test.sqlite3`. La tabla de usuarios contiene el hash bcrypt de `ralph`, que se crackea y funciona en LimeSurvey.

## Foothold

LimeSurvey permite subir plugins como ZIP. Se crea un plugin con una función que ejecuta comandos y se activa desde la interfaz; al llamarlo se obtiene un webshell como `www-data`. La configuración de LimeSurvey contiene la contraseña de PostgreSQL, que se prueba contra los usuarios del sistema y funciona para `ron`.

```bash
# traversal
curl --path-as-is -H 'Authorization: Bearer <JWT>' \
  'http://api.heal.htb/download?filename=../../storage/development.sqlite3' -o dev.sqlite3
# Consul
curl -X PUT http://127.0.0.1:8500/v1/agent/service/register -d @svc.json
/tmp/root -p```

## Movimiento lateral

`ron` entra por SSH. `ps` muestra un agente Consul como root escuchando en `127.0.0.1:8500`.

## Escalada de privilegios

Consul no requiere ACL. Se registra un servicio con un `Check` cuyos `args` copian bash a `/tmp` y le dan SUID; el agente ejecuta el check periódicamente como root. Después se lanza la copia con `-p`.

## Evidencia

- Traversal en `/download`.
- Bases SQLite y hash de `ralph`.
- Plugin de LimeSurvey y shell `www-data`.
- Contraseña de PostgreSQL reutilizada por `ron`.
- Servicio Consul con check root.

## Lecciones aprendidas

- Un endpoint de descarga debe resolver y confinar la ruta.
- Los hashes de la aplicación pueden reutilizarse en otro servicio.
- Los plugins de CMS son código ejecutable.
- Consul sin ACL en localhost sigue siendo una vía de root.

## Mitigación y detección

- Normalizar y validar rutas con listas blancas.
- No reutilizar contraseñas entre servicios.
- Firmar y revisar plugins; restringir su carga.
- Habilitar ACLs en Consul y no ejecutar checks como root.

## Referencias

- [0xdf — Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html)
- [IppSec — Heal](https://www.youtube.com/watch?v=7KsIks7bdp8)
- [Hack The Box — Heal](https://app.hackthebox.com/machines/heal)
