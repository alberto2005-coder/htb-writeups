---
topic: CloudTrail
tags: [cloud, aws, cloudtrail, logging, iam, incident-response]
---

# CloudTrail

[🌐 English](cloudtrail.en.md) | **Español**

## Concepto

CloudTrail registra llamadas a la API de AWS: quién, desde dónde, qué recurso y con qué resultado. Es la fuente principal para investigar accesos a IAM, S3, EC2 y servicios de datos, y para distinguir actividad legítima de una cuenta comprometida.

## Cuándo aplica

- Investigación de una cuenta AWS.
- Accesos anómalos a S3 o IAM.
- Creación de usuarios, claves o roles.
- Correlación con VPC Flow Logs y GuardDuty.

## Procedimiento

1. Confirmar que CloudTrail está habilitado en todas las regiones.
2. Buscar eventos por identidad, IP y rango temporal.
3. Revisar `errorCode`, `userAgent` y `sourceIPAddress`.
4. Correlacionar con S3, IAM y EC2.
5. Exportar la evidencia y reconstruir la cadena.

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateAccessKey
aws cloudtrail lookup-events --start-time 2026-11-01 --end-time 2026-11-02
aws s3api get-bucket-logging --bucket <BUCKET>
```

## Variantes

- Event history frente a un trail a S3/CloudWatch.
- Data events de S3 y Lambda.
- Actividad de una clave de acceso filtrada.
- Cambios de política y creación de roles.

## Limitaciones

- La retención por defecto es limitada.
- Los data events pueden no estar habilitados.
- Un atacante con permisos puede alterar el trail.
- Las IPs pueden ser de servicios intermedios.

## Mitigación y detección

- Trail multi-región con integridad y retención.
- Alertas de IAM, S3 y cambios de logging.
- MFA y rotación de claves.
- Correlación con GuardDuty y Security Hub.

## Referencias

- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html>
- <https://attack.mitre.org/techniques/T1562/008/>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html>
