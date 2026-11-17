---
machine: Seventeen
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, docker, roundcube, npm, privesc]
---

# Seventeen — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El vhost `exam.seventeen.htb` tiene una SQLi booleana en `?p=take_exam&id=`. Volcando `erms_db` y `db_sfms` se obtiene el número de estudiante y la contraseña de Kelly, con los que se entra en School File Management System. La aplicación permite subir un PHP; el PDF de bienvenida menciona un webmail en `mastermailer.seventeen.htb`. Roundcube 1.4.2 es vulnerable a CVE-2020-12640: el instalador incluye una ruta controlada como plugin y ejecuta el archivo. Se sube `papers.php` a una carpeta conocida y se apunta el instalador a `papers`, lo que da una shell `www-data` en un contenedor. Los archivos de configuración filtran credenciales de MySQL y la contraseña de `mark`, que reutiliza en SSH. El módulo npm `db-logger` contiene la contraseña de `kavi`; `kavi` puede ejecutar `/opt/app/startup.sh` como root, y el script instala `loglevel` desde el registro configurado en `/home/kavi/.npmrc`. Publicando un `loglevel` malicioso en un Verdaccio propio se escribe una clave SSH en `/root/.ssh/authorized_keys`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8000 <IP>
```

- `22` OpenSSH 7.6p1 Ubuntu 18.04.
- `80` Apache 2.4.29 con la web de una empresa educativa.
- `8000` Apache 2.4.38 en un contenedor; devuelve `403`.

```bash
echo '<IP> seventeen.htb exam.seventeen.htb oldmanagement.seventeen.htb mastermailer.seventeen.htb' \
  | sudo tee -a /etc/hosts
```

`wfuzz` de vhosts descubre `exam`. `feroxbuster` encuentra `/admin`, `/uploads`, `/database` y `/classes`.

## Enumeración

La web de exámenes usa `/?p=take_exam&id=1`. Una comilla cambia la respuesta; `id=1' AND 4755=4755 AND 'a'='a` devuelve la página normal y `4755=4756` devuelve «Unknown Exam ID». Es una SQLi booleana. `sqlmap --technique B` enumera cuatro bases: `erms_db`, `db_sfms`, `roundcubedb` e `information_schema`.

```bash
sqlmap -u 'http://exam.seventeen.htb/?p=take_exam&id=1' -p id --technique B --batch --dbs
```

`db_sfms.student` contiene el número `31234` y un hash MD5 que se crackea. Con esas credenciales se entra en School File Management System.

## Foothold

La aplicación permite subir archivos y descargar el PDF de bienvenida, que menciona `https://mastermailer.seventeen.htb/`. El webmail es Roundcube 1.4.2. Su instalador acepta `_plugins_qwerty` y lo usa como ruta de plugin; CVE-2020-12640 permite incluir un archivo PHP controlado.

Se sube `papers.php` como `papers.php` en `files/31234/papers/` y se apunta el instalador a la carpeta `papers`:

```text
_plugins_qwerty=../../../../../../../../../var/www/html/oldmanagement/files/31234/papers
```

Al cargar cualquier página de Roundcube se ejecuta la webshell y llega una reverse shell como `www-data` dentro de un contenedor Docker.

## Movimiento lateral

En `/var/www/html` están `employeemanagementsystem`, `mastermailer` y `oldmanagement`. Los archivos de conexión contienen credenciales de MySQL; la de `ems` es también la contraseña de `mark` en el host:

```bash
ssh mark@seventeen.htb
```

En `/var/mail` hay un correo para `kavi` que menciona un registro npm privado y un «old logger». `npm search log --registry http://127.0.0.1:4873` muestra `db-logger`, de `kavigihan`. Al instalar `db-logger` se lee `logger.js`, que contiene una contraseña de MySQL que también es la de `kavi`.

## Escalada de privilegios

`kavi` puede ejecutar `/opt/app/startup.sh` como root. El script comprueba `db-logger` y `loglevel`, instala lo que falte y arranca Node. `~/.npmrc` apunta al registro local, pero puede modificarse para apuntar a un Verdaccio propio.

Se crea un paquete `loglevel` con versión superior a la instalada y un `index.js` que escribe una clave SSH en `/root/.ssh/authorized_keys` y exporta `log`, `debug` y `warn`. Se publica en el Verdaccio propio, se cambia `.npmrc` y se ejecuta:

```bash
sudo /opt/app/startup.sh
```

El script instala el paquete malicioso como root y ejecuta el `require`. Después se entra por SSH como root.

## Evidencia

- Respuesta booleana distinta en `take_exam`.
- Volcado de `db_sfms.student` y login en SFMS.
- PDF con la URL del webmail.
- `papers.php` subido y shell `www-data` en el contenedor.
- Credenciales de MySQL, `mark` y `db-logger`.
- `startup.sh` instalando `loglevel` y clave en `/root/.ssh/authorized_keys`.

## Lecciones aprendidas

- Una SQLi booleana lenta sigue siendo suficiente para volcar varias bases.
- Los documentos de bienvenida y el correo interno revelan servicios y nombres de usuario.
- Un instalador de Roundcube accesible puede convertir un LFI en RCE.
- Los módulos npm con credenciales hardcodeadas filtran contraseñas reutilizadas.
- Un script de arranque que instala dependencias como root ejecuta código de un registro controlable.

## Mitigaciones y detección

- Parametrizar `id` y no mostrar mensajes distintos según la condición.
- Eliminar `/installer` de Roundcube y actualizar a una versión corregida.
- No guardar credenciales en código; usar variables de entorno y un gestor de secretos.
- Bloquear la ejecución PHP en directorios de subida.
- Ejecutar `npm install` sin privilegios, fijar versiones y usar un registro con allowlist.
- Detectar `sqlmap`, accesos a `installer`, subidas PHP, `.npmrc` modificado y paquetes nuevos en `/opt/app/node_modules`.

## Referencias

- [0xdf — Seventeen](https://0xdf.gitlab.io/2022/09/24/htb-seventeen.html)
- [IppSec — Seventeen](https://www.youtube.com/watch?v=U-2nI6wSPOE)
- [NVD — CVE-2020-12640](https://nvd.nist.gov/vuln/detail/CVE-2020-12640)
- [Hack The Box — Seventeen](https://app.hackthebox.com/machines/seventeen)
