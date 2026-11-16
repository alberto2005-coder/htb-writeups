---
machine: Kotarak
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, tomcat, ajp, ghostcat, ssrf, wget, cve-2016-4971, privesc]
---

# Kotarak — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tomcat expone AJP y es vulnerable a Ghostcat, lo que permite leer archivos. Un SSRF en `url.php` alcanza el manager interno y un backup contiene sus credenciales, con las que se despliega un WAR. Con una shell en el contenedor DMZ se extraen `ntds.dit` y el hive SYSTEM y se obtiene la contraseña de `atanas`. En el host, un cron ejecuta `wget` como root; CVE-2016-4971 permite escribir un `.wgetrc` que exfiltra `/etc/shadow` y deja un cron con shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8009,8080,60000 <IP>
```

- `22` OpenSSH, `8009` AJP y `8080` Tomcat 8.5.5.
- `60000` es el host web de Kotarak.
- La web tiene un proxy de URLs y un Tomcat manager.

## Enumeración

El `url.php` de `60000` permite solicitar URLs y devuelve el contenido. Con `http://localhost:8080/manager/html` se llega al manager, y un backup del contenedor contiene las credenciales. Ghostcat (`CVE-2020-1938`) permite leer `WEB-INF/web.xml` y desplegar un WAR con una webshell.

## Foothold

Se sube un WAR con una JSP que ejecuta comandos y se accede a ella desde el puerto `8080`. La shell corre como Tomcat en el contenedor DMZ.

```text
http://<IP>:8080/shell/shell.jsp?cmd=id
```

## Movimiento lateral

Desde el contenedor se copian `ntds.dit` y el hive SYSTEM a `/tmp`, se extraen con `secretsdump.py` y se obtiene el hash de `atanas`. La contraseña crackeada permite SSH al host real.

## Escalada de privilegios

El host ejecuta `wget` como root desde un cron. Wget 1.16 es vulnerable a CVE-2016-4971: ante una redirección HTTP a FTP guarda el archivo remoto con el nombre original. Se sirve un `.wgetrc` con `post_file = /etc/shadow` y `output_document = /etc/cron.d/wget-root-shell`; la siguiente ejecución exfiltra el hash y escribe un cron que devuelve una shell de root.

```text
post_file = /etc/shadow
output_document = /etc/cron.d/wget-root-shell
```

## Evidencia

- `WEB-INF/web.xml` leído por AJP.
- WAR desplegado y shell como Tomcat.
- `ntds.dit` y SYSTEM volcados.
- `.wgetrc` en la home de root y cron con shell de root.

## Lecciones aprendidas

- AJP no debe estar expuesto ni sin `secret`.
- Un SSRF puede alcanzar el manager de Tomcat en localhost.
- Los backups de contenedores conservan credenciales y bases de AD.
- Una redirección HTTP→FTP en wget rompe la validación del nombre de archivo.

## Mitigación y detección

- Cerrar AJP o exigir `secret` y `address` en el conector.
- Actualizar Wget a 1.18 o superior y no ejecutarlo como root desde cron.
- Restringir el manager a localhost y rotar credenciales de backups.
- Monitorizar `.wgetrc`, redirecciones a FTP y escrituras en `/etc/cron.d`.

## Referencias

- [0xdf — Kotarak](https://0xdf.gitlab.io/2021/05/19/htb-kotarak.html)
- [IppSec — Kotarak](https://www.youtube.com/watch?v=38e-sxPWiuY)
- [Hack The Box — Kotarak](https://app.hackthebox.com/machines/kotarak)
