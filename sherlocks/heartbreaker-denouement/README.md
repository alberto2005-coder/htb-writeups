---
sherlock: Heartbreaker-Denouement
domain: Cloud
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [cloud, aws, cloudtrail, ssrf, imds, rds, exfiltration]
---

# Heartbreaker-Denouement — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un cliente reporta que datos suyos se ofrecen en un mercado de la darknet. La única pista inicial es una credencial de AWS comprometida. Se entrega una colección UAC del servidor web y los logs de CloudTrail: hay que determinar si hubo exfiltración y reconstruir la cadena.

La investigación termina lejos del servidor: el actor no vuelve a tocar la máquina, mueve dos bases de datos RDS a su propia cuenta mediante la API de AWS.

## Evidencias

```text
uac                      tarball del servidor web
├── access.log           Apache, peticiones y códigos
├── error.log            mensajes de la aplicación (incluye entradas del usuario)
├── .bash_history
├── .mysql_history       consultas del cliente MySQL
└── webroot/             código de la aplicación

cloudtrail/              ~9.000 JSON gzip, uno por evento
```

```bash
tar xzf uac -C work/tar
gzip -dc cloudtrail/*.json.gz > work/ct/all.jsonl     # o merge con Python
```

## Investigación

### 1. Reconocimiento y entrada

En `access.log` aparece una IP externa con cientos de peticiones a rutas de diccionario, casi todas `404`: **wordlist scanning** (T1595.003). El ruido se rompe cuando una ruta devuelve `301` y revela la aplicación real.

En `error.log`, las líneas `Input:` muestran que la página pasa el valor del usuario a `file_get_contents`. Primero lee ficheros locales con `file:///`; después apunta a `http://169.254.169.254`, el servicio de metadatos de la instancia. Es un **SSRF** (T1190) que alcanza un destino solo enrutable desde la VM.

```bash
grep -c ' 404 ' access.log
grep -vE ' 404 ' access.log | grep -E ' 30[0-9] '
grep 'Input:' error.log | head
grep -r '169.254.169.254' error.log access.log
```

### 2. Credenciales y descubrimiento

El SSRF devuelve las credenciales del rol de la instancia. En paralelo, una clave de usuario IAM filtrada se usa desde las mismas IPs. Con CloudTrail fusionado en JSONL, el patrón es:

```bash
python3 summarize_ct.py work/ct/all.jsonl --user devops-ash --by eventName
python3 summarize_ct.py work/ct/all.jsonl --user devops-ash --success --by awsRegion
```

- `GetCallerIdentity` es el "whoami" de AWS: no requiere permisos y confirma a quién pertenecen las claves (T1033).
- `DescribeInstances` lista instancias y sus IPs públicas, coherente con el reconocimiento previo (T1580).
- Las llamadas del usuario IAM tienen éxito en **dos** regiones; contar todas las regiones desde las IPs del atacante mezcla las credenciales del rol y da un número mayor.

### 3. Colección y exfiltración

`CreateDBSnapshot` sobre dos bases de producción (T1578.001), con la fecha en el nombre del snapshot. Después, `ModifyDBSnapshotAttribute` añade una cuenta ajena a `valuesToAdd`: el snapshot se comparte con la cuenta del atacante y la copia ocurre dentro de AWS (T1537).

```bash
python3 summarize_ct.py work/ct/all.jsonl --event CreateDBSnapshot \
  --field requestParameters.dBSnapshotIdentifier
python3 summarize_ct.py work/ct/all.jsonl --event ModifyDBSnapshotAttribute \
  --field requestParameters.valuesToAdd
```

Los fallos también cuentan: cientos de `AccessDenied` desde las IPs del actor son el rastro de la enumeración de permisos.

## Conclusiones

- La entrada fue un SSRF en una página PHP; el destino, el servicio de metadatos, entregó credenciales de rol.
- La clave IAM filtrada y el rol de instancia se usaron desde fuera; CloudTrail permite separarlos por `userIdentity.arn`.
- La exfiltración no necesita acceso al servidor: snapshots de RDS compartidos con otra cuenta.
- Defensas clave: bloquear esquemas y hosts en las peticiones del servidor, exigir **IMDSv2** con hop limit 1, rotar claves filtradas y alertar sobre `ModifyDBSnapshotAttribute` con cuentas externas.

## Referencias

- <https://labs.hackthebox.com/sherlocks/heartbreaker-denouement>
- <https://inksec.io/blue-team/sherlocks/heartbreaker-denouement>
- <https://www.moamenbasel.com/htb-writeups/sherlocks>
- <https://attack.mitre.org/techniques/T1537/>
