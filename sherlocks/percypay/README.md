---
sherlock: PercyPay
category: Cloud
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [cloud, aws, cloudtrail, lambda, iam, exfiltration]
---

# PercyPay — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una empresa de pagos detecta accesos anómalos en su cuenta de AWS. Se entregan registros de CloudTrail y de la función Lambda para reconstruir la exposición de credenciales, la escalada y la exfiltración de datos de clientes.

## Evidencias

- CloudTrail de la cuenta y de la región afectadas.
- Logs de ejecución de Lambda.
- Eventos de IAM y de configuración de funciones.
- Registros de acceso a almacenamiento y de salida de red.

```bash
aws cloudtrail lookup-events --region <REGION> --max-results 50
```

## Investigación

### 1. Inventario y triaje

Se identifican las identidades que actuaron, las claves usadas y las regiones. Los eventos `AssumeRole`, `GetSecretValue` y `UpdateFunctionConfiguration` son prioritarios.

```bash
jq -r '.Records[] | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' cloudtrail.json
```

### 2. Línea temporal

- Exposición inicial de una clave o de un rol.
- Cambio de política o de variables de entorno de Lambda.
- Invocaciones anómalas y acceso a recursos de datos.
- Transferencia fuera de la cuenta.

La hora de CloudTrail es UTC; se conserva así para no mezclar zonas.

### 3. Artefacto clave

La función Lambda modificada contenía la ruta de escalada: una variable de entorno con credenciales o un rol excesivamente permisivo. El análisis del código y de las invocaciones muestra cómo se usó para leer y enviar datos.

```bash
aws lambda get-function-configuration --function-name <FUNCTION>
aws lambda get-function --function-name <FUNCTION>
```

## Conclusiones

- Qué identidad quedó expuesta y cómo se reutilizó.
- Qué política o variable permitió la escalada.
- Qué datos se leyeron y hacia dónde salieron.
- IOCs: ARN, IP, función y bucket, redactados.

## Lecciones

- CloudTrail aporta la identidad, pero el código de Lambda explica el impacto.
- Las variables de entorno son parte de la superficie de secretos.
- Una política de rol amplia puede convertir una lectura en exfiltración.

## Referencias

- <https://www.hackthebox.com/sherlocks/PercyPay>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference.html>
- <https://attack.mitre.org/techniques/T1078/004/>
