---
sherlock: OpTinselTrace-2
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, cloud, aws, cloudtrail, s3, iam]
---

# OpTinselTrace-2 — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

Continuación de OpTinselTrace-1. El binario enviado por el insider contenía credenciales de una cuenta AWS. Se entrega un conjunto de CloudTrail (más de 22.000 eventos) y artefactos del caso anterior; hay que reconstruir el acceso a la nube, los buckets y los permisos utilizados.

## Evidencias

- Exportación de CloudTrail en JSON/JSONL.
- Artefactos del caso 1 (binario, correo, credenciales).
- Lista de buckets y objetos accedidos.
- Eventos de IAM, STS y S3.

```bash
sha256sum optinseltrace-2.zip
find . -type f -maxdepth 3 | head -30
```

## Investigación

### 1. Inventario y triaje

Se identifica el formato y el rango temporal:

```bash
jq -r '.Records[]? | [.eventTime,.eventSource,.eventName] | @tsv' cloudtrail.json | head
jq -r '.Records[]?.eventName' cloudtrail.json | sort | uniq -c | sort -nr | head
```

Se buscan eventos de `sts:GetCallerIdentity`, `s3:ListBucket`, `s3:GetObject`, `iam:CreateAccessKey` y `iam:AttachUserPolicy`.

### 2. Línea temporal

- Uso inicial de la clave filtrada.
- Enumeración de buckets y objetos.
- Descarga de datos o creación de nuevas claves.
- Cambios de permisos o persistencia en IAM.

```bash
jq -r '.Records[]? | select(.eventSource=="s3.amazonaws.com") |
  [.eventTime,.userIdentity.arn,.eventName,.requestParameters.bucketName,.requestParameters.key] | @tsv' cloudtrail.json
```

### 3. Artefacto clave

La clave de acceso del binario aparece en `userIdentity.accessKeyId`. Se correlaciona con la IP de origen y con el `userAgent`. Los eventos de S3 muestran qué objetos se listaron/descargaron y si se compartió un snapshot o un bucket.

```text
binario -> accessKeyId -> CloudTrail -> S3/IAM
```

## Conclusiones

- La credencial AWS del binario se usó para enumerar y acceder a S3.
- El atacante pudo crear claves o modificar políticas para persistir.
- Los IOCs son `accessKeyId`, IP de origen, user-agent, bucket y objetos.
- La rotación de la clave y la revisión de políticas son obligatorias.

## Lecciones

- CloudTrail es la fuente principal para reconstruir actividad AWS.
- `userIdentity.accessKeyId` enlaza el binario con la cuenta.
- S3 puede filtrar datos sin desplegar malware.
- Una clave en un binario es un secreto comprometido para siempre.

## Referencias

- <https://inksec.io/blue-team/sherlocks/optinseltrace-2>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html>
- <https://attack.mitre.org/techniques/T1078/004/>
