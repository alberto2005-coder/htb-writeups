---
topic: Acceso a credenciales en DynamoDB
tags: [cloud, aws, dynamodb, credentials, enumeration]
---

# Acceso a credenciales en DynamoDB

[🌐 English](dynamodb-credential-access.en.md) | **Español**

## Concepto

Una tabla DynamoDB expuesta contiene usuarios, tokens o contraseñas que se reutilizan contra otros servicios. La CLI permite listar y escanear tablas si se dispone de credenciales o de un endpoint local que simula AWS.

## Cuándo aplica

- Credenciales AWS en código, variables de entorno o metadatos.
- Endpoints locales que emulan S3/DynamoDB durante el desarrollo.
- Aplicaciones que guardan secretos en tablas sin cifrado de campo.

## Procedimiento

1. Identificar el endpoint y las credenciales disponibles.
2. Listar tablas con `aws dynamodb list-tables`.
3. Describir la tabla y escanear sus elementos.
4. Probar los valores recuperados contra SSH, paneles o APIs.

```bash
aws --endpoint-url http://<HOST> dynamodb list-tables
aws --endpoint-url http://<HOST> dynamodb describe-table --table-name users
aws --endpoint-url http://<HOST> dynamodb scan --table-name users
aws --endpoint-url http://<HOST> dynamodb get-item --table-name users \
  --key '{"username":{"S":"admin"}}'
```

## Variantes

- Credenciales de instancia o rol IAM en lugar de claves estáticas.
- Tablas con nombres de usuario como clave de partición.
- Exportaciones a S3 o streams con datos históricos.
- Endpoints locales de LocalStack o MOTD.

## Limitaciones

- Sin permisos `dynamodb:Scan` no se puede volcar la tabla.
- Los valores pueden estar cifrados con KMS.
- El endpoint debe ser accesible desde la red del atacante.

## Mitigación y detección

- Aplicar mínimo privilegio IAM y evitar `Scan` en producción.
- No guardar contraseñas en claro; usar KMS y hashes lentos.
- Rotar credenciales y monitorizar accesos anómalos a tablas.

## Referencias

- <https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Scan.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html>
- <https://attack.mitre.org/techniques/T1580/>
