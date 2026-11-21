---
machine: Fingerprint
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, hql, hibernate, xss, java-deserialization, jwt, aes-ecb, cmatch, privesc]
---

# Fingerprint — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Cadena larga en varias etapas. Un *execute after redirect* (EAR) y un directory traversal en `/admin` dan lectura de archivos; el análisis del código revela inyección HQL (Hibernate) y un XSS. Con la inyección booleana se extraen datos, se genera un payload Java serializado a medida y se abusa de un secreto JWT compartido para ejecutar y obtener shell como `www-data`. Para pasar a `john` se explota el SUID `cmatch`, que cuenta coincidencias regex en cualquier archivo y sirve de oráculo para extraer su clave SSH. Ya como `john` se accede al backup de la aplicación segura de `/root`. Esa aplicación usa AES-ECB con el secreto anexado al usuario, lo que permite un ataque byte a byte sobre ECB para filtrar el secreto, firmar una cookie de administrador, usar una lectura de archivos y llegar por SSH a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
```

- `22`: OpenSSH 7.6p1 Ubuntu.
- `80`: Werkzeug 1.0.1 sobre Python 2.7.17, aplicación Flask.
- `8080`: Sun GlassFish 5.0.1, aplicación Java.

```bash
echo '<IP> fingerprint.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://fingerprint.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio Flask tiene login, registro y un panel `/admin` que muestra logs. El parámetro del visor de logs permite salir del directorio previsto y leer archivos. Al registrarse, la aplicación redirige y procesa datos antes de comprobar la sesión (EAR), lo que facilita el acceso a partes internas.

El análisis del código y del tráfico muestra:

- Consultas HQL construidas con entrada del usuario.
- Un XSS en el perfil.
- Un secreto JWT compartido entre la aplicación Flask y la Java.
- Una tabla de usuarios con un campo oculto que se puede extraer con inyección booleana.

## Foothold

Con la inyección HQL se enumeran usuarios y campos. Para ejecutar código se prepara un proyecto Maven que genere un objeto Java serializado con la librería disponible en GlassFish y se firma un JWT válido para la aplicación Java. El payload se envía a un endpoint que deserializa, y la cadena termina en una shell como `www-data`.

```bash
mvn clean package
java -cp target/<ARTIFACT>.jar <MAIN_CLASS> '<COMMAND>'
```

La shell permite leer el código de las dos aplicaciones y confirmar el secreto compartido.

## Movimiento lateral

`www-data` puede ejecutar `/usr/bin/cmatch` como `john`. El binario recibe dos argumentos: un archivo y una expresión regular, y devuelve cuántas coincidencias hay. Es SUID, así que lee archivos que `www-data` no puede abrir, y la cuenta de coincidencias se convierte en un oráculo para extraer el contenido byte a byte.

Se usa para leer `/home/john/.ssh/id_rsa` y reconstruir la clave privada; después se entra por SSH como `john`.

```bash
cmatch /home/john/.ssh/id_rsa '^-----BEGIN'
cmatch /home/john/.ssh/id_rsa '^<PREFIJO>'
```

## Escalada de privilegios

`john` puede leer `/var/backups/flask-app-secure.bak`, un ZIP con el código de la aplicación que corre como root en `8088`. El código construye `usuario,secreto,true|false` y lo cifra con AES-ECB. Como ECB cifra bloques iguales de forma igual, se puede hacer un ataque byte a byte: se elige un nombre de usuario de longitud controlada y se comparan los bloques de las cookies para recuperar el secreto carácter a carácter.

Con el secreto se firma una cookie de administrador, se usa la lectura de archivos de la aplicación segura para leer la clave SSH de root y se entra por SSH.

```bash
python3 exploit_ecb.py --url http://127.0.0.1:8088
curl -s http://127.0.0.1:8088/admin -H 'Cookie: <COOKIE>'
```

## Evidencia

- Traversal en `/admin` y lectura de `/etc/passwd` y del código.
- Inyección HQL con respuestas booleanas.
- JWT firmado con el secreto compartido y shell como `www-data`.
- `cmatch` SUID y extracción de la clave de `john`.
- Backup `flask-app-secure.bak` y análisis del cifrado AES-ECB.
- Secreto recuperado, cookie de administrador y lectura de la clave de root.
- `id` con UID 0.

## Lecciones aprendidas

- Encadenar vulnerabilidades menores (EAR, traversal, XSS) puede abrir una ejecución.
- HQL no es SQL: la sintaxis y los objetos cambian, pero la inyección sigue siendo posible.
- Un binario SUID que revela información puede ser un oráculo de lectura.
- AES-ECB filtra patrones y no debe usarse para cookies o identificadores.
- Un backup de una aplicación privilegiada es código fuente y, a menudo, la clave del root.

## Mitigaciones y detección

- Parametrizar HQL y validar tipos; no concatenar entrada en consultas.
- Corregir el orden de comprobaciones para que la sesión se valide antes de procesar datos.
- Escapar el perfil y usar cookies `HttpOnly`, `Secure` y `SameSite`.
- Retirar SUID innecesarios y revisar binarios que leen archivos arbitrarios.
- Sustituir AES-ECB por AES-GCM con IV aleatorio y autenticación.
- Proteger los backups de aplicaciones privilegiadas y no mezclar secretos entre servicios.
- Alertar de lecturas de claves SSH y de accesos a `/console` o paneles internos.

## Referencias

- [0xdf — Fingerprint](https://0xdf.gitlab.io/2022/05/14/htb-fingerprint.html)
- [IppSec — Fingerprint](https://www.youtube.com/watch?v=YBabDbyk3eo)
- [Hack The Box — Fingerprint](https://app.hackthebox.com/machines/fingerprint)
- [Knowledge — Inyección HQL](../../../knowledge/web/hql-injection.md)
