---
machine: UpDown
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ssrf, git-dumper, vhosts, sudo, apt]
---

# UpDown — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una web comprueba si una URL responde y es vulnerable a SSRF. El código fuente expuesto en un repositorio Git revela un virtual host interno y una función de ejecución. Las credenciales obtenidas permiten SSH; una regla `sudo` sobre una herramienta de gestión de paquetes permite root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://<IP> -H 'Host: FUZZ.updown.htb' -w <WORDLIST>
```

- SSH y Apache.
- La aplicación principal comprueba el estado de una URL.
- Hay virtual hosts y un repositorio Git accesible.

## Enumeración

- `/.git/` existe y se puede extraer con `git-dumper`.
- El código muestra una petición HTTP iniciada por el servidor y una lista de hosts permitidos.
- El vhost de desarrollo revela credenciales o una ruta de administración.
- El acceso SSH usa un usuario con una regla `sudo` concreta.

## Foothold

Se usa la funcionalidad de comprobación para solicitar un recurso interno y confirmar SSRF. Con el código fuente se identifican parámetros y rutas no visibles; las credenciales del vhost permiten entrar por SSH.

```bash
git-dumper http://<IP>/.git/ ./src
curl -s 'http://<IP>/check' --data-urlencode 'url=http://127.0.0.1:80/'
```

## Escalada de privilegios

`sudo -l` muestra un binario de gestión de paquetes o un script con una opción que permite ejecutar un comando. Se prepara un paquete/archivo local y se invoca la regla sin modificar el sistema fuera del laboratorio.

```bash
sudo -l
sudo <BINARIO> --help
```

## Evidencia

- Respuesta del servidor a una URL interna.
- Repositorio Git extraído y código vulnerable.
- Sesión SSH con el usuario encontrado.
- Ejecución controlada mediante `sudo` y root.

## Lecciones aprendidas

- Un comprobador de URLs puede convertirse en SSRF.
- Un `.git` expuesto filtra código, rutas y credenciales.
- Los virtual hosts internos no deben confiar en el filtrado del host principal.
- Las reglas `sudo` sobre gestores de paquetes son peligrosas.

## Mitigaciones y detección

- Bloquear esquemas y rangos internos en el comprobador.
- No publicar `.git`, backups ni entornos de desarrollo.
- Auditar `sudo -l` y limitar opciones que ejecutan comandos.
- Alertar de peticiones a `127.0.0.1` y descargas de repositorios.
- Referencias: OWASP SSRF, GTFOBins, HTB UpDown.

## Referencias

- <https://www.hackthebox.com/machines/UpDown>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://gtfobins.github.io/>
- <https://attack.mitre.org/techniques/T1552/>
