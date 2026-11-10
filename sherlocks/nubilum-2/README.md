---
sherlock: Nubilum-2
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
state: Retired
evidence: CloudTrail de una cuenta con un bucket S3 expuesto
tools: [jq, Splunk, AWS CLI]
tags: [dfir, cloud, aws, s3, iam, cloudtrail]
---

# Nubilum-2 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Forela usa **S3** como almacén y lago de datos. Un usuario reporta que no puede acceder a los ficheros de un directorio concreto y se sospecha de una **política de bucket mal configurada** en `forela-fileshare`. Hay que reconstruir qué hizo el intruso y por qué el usuario legítimo perdió el acceso.

## Evidencias

- Logs de **CloudTrail** de la cuenta `949622803460`, en JSON comprimido por región.

## Investigación

### 1. Preparar

```bash
jq -s '[.[].Records[]] | sort_by(.eventTime) | unique_by(.eventID)' CloudTrail/*/*.json > merged.json
jq -r '.[] | [.eventTime,.eventName,.userIdentity.type,.sourceIPAddress,.errorCode] | @tsv' merged.json | sort > timeline.tsv
```

### 2. El origen

El `userAgent` distingue al atacante del tráfico normal: un `aws-cli` reciente lanzado desde una distribución de pentest identifica las llamadas manuales. Con eso se aísla la IP de origen y la ventana.

```bash
jq -r '.[] | "\(.sourceIPAddress)\t\(.userAgent)"' merged.json | sort -u | grep -i "aws-cli"
```

### 3. La fuga inicial

Lecturas **anónimas** (`userIdentity.type = AWSAccount`/`Anonymous`) sobre objetos del bucket: el atacante descarga un CSV de claves de acceso sin autenticarse. Ése es el punto de partida de todo.

```bash
jq -r '.[] | select(.eventName=="GetObject") | [.eventTime,.userIdentity.type,.requestParameters.key] | @tsv' merged.json | grep -i "accesskeys\|credential"
```

### 4. Escalada con las claves robadas

Con las claves del CSV, el actor encadena decenas de llamadas **denegadas** (`AccessDenied`) hasta encontrar un permiso útil, y termina escribiendo una **política inline sobre sí mismo** para ampliar privilegios.

```bash
jq -r '.[] | select(.errorCode=="AccessDenied") | .eventName' merged.json | sort | uniq -c | sort -rn
jq -r '.[] | select(.eventName|test("PutUserPolicy|AttachUserPolicy|CreateAccessKey|PutBucketPolicy")) | [.eventTime,.eventName,.userIdentity.arn] | @tsv' merged.json
```

### 5. Impacto en el negocio

El usuario legítimo deja de ver sus ficheros porque los objetos acaban cifrados con una clave KMS sobre la que no tiene `kms:Decrypt`. Los `AccessDenied` en `kms:Decrypt` y los cambios de ACL/política del bucket explican la incidencia del helpdesk.

## Conclusiones

- Entrada: bucket con lectura pública y un CSV de claves IAM dentro.
- Escalada: sondeo con `AccessDenied` hasta dar con un permiso de escritura de políticas.
- Persistencia: clave de acceso creada y política inline autoasignada.
- Impacto: pérdida de acceso del usuario legítimo por cambios de política y de cifrado.

## Lecciones

- Un bucket público con credenciales dentro es un compromiso de cuenta, no una fuga de datos.
- Los `AccessDenied` son evidencia: dibujan el reconocimiento del atacante.
- `PutUserPolicy` sobre el propio usuario es escalada de privilegios silenciosa y debe alertarse.
- La incidencia del helpdesk suele ser la punta: el cambio de política es la causa.

## Nota de dificultad

El índice la recoge como **Medium**; alguna fuente pública la lista como **Easy**. Se mantiene Medium y se anota la discrepancia.
