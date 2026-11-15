---
topic: Acceso a credenciales en DynamoDB
tags: [cloud, aws, dynamodb, credentials, enumeration]
---

# Acceso a credenciales en DynamoDB

**English** | [🇪🇸 Español](dynamodb-credential-access.md)

## Concept

An exposed DynamoDB table holds users, tokens or passwords reused against other services. The CLI can list and scan tables when credentials are available or when a local endpoint emulates AWS.

## When it applies

- AWS credentials in code, environment variables or metadata.
- Local endpoints emulating S3/DynamoDB during development.
- Applications storing secrets in tables without field-level encryption.

## Procedure

1. Identify the endpoint and available credentials.
2. List tables with `aws dynamodb list-tables`.
3. Describe the table and scan its items.
4. Test recovered values against SSH, panels or APIs.

```bash
aws --endpoint-url http://<HOST> dynamodb list-tables
aws --endpoint-url http://<HOST> dynamodb describe-table --table-name users
aws --endpoint-url http://<HOST> dynamodb scan --table-name users
aws --endpoint-url http://<HOST> dynamodb get-item --table-name users \
  --key '{"username":{"S":"admin"}}'
```

## Variants

- Instance or IAM role credentials instead of static keys.
- Tables keyed by username.
- S3 exports or streams with historical data.
- LocalStack or custom local endpoints.

## Limitations

- Without `dynamodb:Scan` permission the table cannot be dumped.
- Values may be KMS-encrypted.
- The endpoint must be reachable from the attacker network.

## Mitigation and detection

- Enforce least-privilege IAM and avoid `Scan` in production.
- Do not store plaintext passwords; use KMS and slow hashes.
- Rotate credentials and monitor anomalous table access.

## References

- <https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Scan.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html>
- <https://attack.mitre.org/techniques/T1580/>
