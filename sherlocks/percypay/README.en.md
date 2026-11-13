---
sherlock: PercyPay
category: Cloud
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [cloud, aws, cloudtrail, lambda, iam, exfiltration]
---

# PercyPay — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A payments company detects anomalous access in its AWS account. CloudTrail and Lambda logs are provided to reconstruct credential exposure, privilege escalation and customer-data exfiltration.

## Evidence

- CloudTrail for the affected account and region.
- Lambda execution logs.
- IAM and function-configuration events.
- Storage access and network egress records.

```bash
aws cloudtrail lookup-events --region <REGION> --max-results 50
```

## Investigation

### 1. Inventory and triage

Identify the acting identities, keys and regions. `AssumeRole`, `GetSecretValue` and `UpdateFunctionConfiguration` events are high priority.

```bash
jq -r '.Records[] | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' cloudtrail.json
```

### 2. Timeline

- Initial exposure of a key or role.
- Policy or Lambda environment-variable change.
- Anomalous invocations and data-resource access.
- Transfer outside the account.

CloudTrail time is UTC; keep it that way to avoid mixing timezones.

### 3. Key artefact

The modified Lambda contained the escalation path: an environment variable with credentials or an overly permissive role. Code and invocation analysis show how it was used to read and send data.

```bash
aws lambda get-function-configuration --function-name <FUNCTION>
aws lambda get-function --function-name <FUNCTION>
```

## Conclusions

- Which identity was exposed and how it was reused.
- Which policy or variable enabled escalation.
- Which data was read and where it went.
- IOCs: ARN, IP, function and bucket, redacted.

## Lessons

- CloudTrail gives identity, but Lambda code explains impact.
- Environment variables are part of the secret surface.
- A broad role policy can turn a read into exfiltration.

## References

- <https://www.hackthebox.com/sherlocks/PercyPay>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-event-reference.html>
- <https://attack.mitre.org/techniques/T1078/004/>
