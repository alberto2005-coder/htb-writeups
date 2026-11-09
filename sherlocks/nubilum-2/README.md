---
sherlock: Nubilum-2
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
evidence: CloudTrail de una cuenta con un bucket S3 expuesto
tools: [jq, Splunk, AWS CLI]
state: Retired
tags: [dfir, cloud-/-aws]
---


# Nubilum-2 — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Forela usa **S3** como almacén y lago de datos. Un usuario reporta que no puede acceder a los ficheros de un directorio y se sospecha de una **política de bucket mal configurada** en `forela-fileshare` que dejó objetos públicos. Hay que reconstruir qué hizo el intruso.

## Evidencias

- Logs de **CloudTrail** de la cuenta (ficheros JSON, muchos).

## Investigación

1. **Preparar**: cargar los JSON en un SIEM (Splunk/Elastic) o normalizar con `jq`.

```bash
jq -r '[.eventTime,.eventName,.userIdentity.type,.userIdentity.arn,.sourceIPAddress,.errorCode]|@tsv' *.json \
  | sort > timeline.tsv
```

2. **Entrada**: cambios de política y de ACL del bucket (`PutBucketPolicy`, `PutBucketAcl`, `PutObjectAcl`) y quién los hizo.

3. **Identidad**: creación de claves de acceso (`CreateAccessKey`) para un usuario existente —el patrón clásico de persistencia— y desde qué IP.

4. **Actividad sobre objetos**: `ListObjects`, `GetObject`, `DeleteObject`; los `AccessDenied` en `kms:Decrypt` explican por qué el usuario legítimo dejó de ver sus ficheros.

5. **Cierre**: qué objetos se expusieron o borraron, en qué ventana y con qué identidad.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- Una política de bucket permisiva convierte datos internos en públicos sin tocar IAM.
- Crear una clave de acceso es persistencia silenciosa en AWS.
- Los `AccessDenied` también son evidencia: cuentan el impacto en el negocio.
- El análisis cloud se hace con consultas, no abriendo ficheros uno a uno.

## Tropiezos

- **Codificación**: algunos exports vienen con los JSON en una sola línea o en `Records[]`; desenvolverlos primero.
- **Duplicados**: las entregas de logs pueden repetir eventos; deduplicar por `eventID`.
- **`kms:Decrypt`**: sin ese permiso, un objeto "público" sigue sin poder leerse.
