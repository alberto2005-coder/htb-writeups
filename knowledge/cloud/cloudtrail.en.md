---
topic: CloudTrail
tags: [cloud, aws, cloudtrail, logging, iam, incident-response]
---

# CloudTrail

**English** | [🇪🇸 Español](cloudtrail.md)

## Concept

CloudTrail records AWS API calls: who, from where, which resource and with what result. It is the primary source for investigating IAM, S3, EC2 and data-service access, and for separating legitimate activity from a compromised account.

## When it applies

- Investigation of an AWS account.
- Anomalous S3 or IAM access.
- Creation of users, keys or roles.
- Correlation with VPC Flow Logs and GuardDuty.

## Procedure

1. Confirm CloudTrail is enabled in all regions.
2. Search events by identity, IP and time range.
3. Review `errorCode`, `userAgent` and `sourceIPAddress`.
4. Correlate with S3, IAM and EC2.
5. Export evidence and reconstruct the chain.

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateAccessKey
aws cloudtrail lookup-events --start-time 2026-11-01 --end-time 2026-11-02
aws s3api get-bucket-logging --bucket <BUCKET>
```

## Variants

- Event history versus a trail to S3/CloudWatch.
- S3 and Lambda data events.
- Activity from a leaked access key.
- Policy changes and role creation.

## Limitations

- Default retention is limited.
- Data events may be disabled.
- An attacker with permissions can alter the trail.
- IPs may belong to intermediate services.

## Mitigation and detection

- Multi-region trail with integrity and retention.
- Alerts on IAM, S3 and logging changes.
- MFA and key rotation.
- Correlation with GuardDuty and Security Hub.

## References

- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html>
- <https://attack.mitre.org/techniques/T1562/008/>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html>
