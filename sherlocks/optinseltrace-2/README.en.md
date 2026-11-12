---
sherlock: OpTinselTrace-2
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, cloud, aws, cloudtrail, s3, iam]
---

# OpTinselTrace-2 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

A follow-up to OpTinselTrace-1. The binary sent by the insider contained AWS credentials. A CloudTrail export (over 22,000 events) and artefacts from the previous case are provided; reconstruct the cloud access, buckets and permissions used.

## Evidence

- CloudTrail export in JSON/JSONL.
- Case 1 artefacts (binary, email, credentials).
- List of buckets and accessed objects.
- IAM, STS and S3 events.

```bash
sha256sum optinseltrace-2.zip
find . -type f -maxdepth 3 | head -30
```

## Investigation

### 1. Inventory and triage

Identify the format and time range:

```bash
jq -r '.Records[]? | [.eventTime,.eventSource,.eventName] | @tsv' cloudtrail.json | head
jq -r '.Records[]?.eventName' cloudtrail.json | sort | uniq -c | sort -nr | head
```

Look for `sts:GetCallerIdentity`, `s3:ListBucket`, `s3:GetObject`, `iam:CreateAccessKey` and `iam:AttachUserPolicy`.

### 2. Timeline

- First use of the leaked key.
- Bucket and object enumeration.
- Data download or new key creation.
- IAM permission changes or persistence.

```bash
jq -r '.Records[]? | select(.eventSource=="s3.amazonaws.com") |
  [.eventTime,.userIdentity.arn,.eventName,.requestParameters.bucketName,.requestParameters.key] | @tsv' cloudtrail.json
```

### 3. Key artefact

The binary's access key appears in `userIdentity.accessKeyId`. Correlate it with the source IP and `userAgent`. S3 events show which objects were listed/downloaded and whether a snapshot or bucket was shared.

```text
binary -> accessKeyId -> CloudTrail -> S3/IAM
```

## Findings

- The binary's AWS credential was used to enumerate and access S3.
- The attacker could create keys or change policies for persistence.
- IOCs are the `accessKeyId`, source IP, user-agent, bucket and objects.
- Key rotation and policy review are mandatory.

## Lessons

- CloudTrail is the primary source for reconstructing AWS activity.
- `userIdentity.accessKeyId` links the binary to the account.
- S3 can leak data without deploying malware.
- A key embedded in a binary is permanently compromised.

## References

- <https://inksec.io/blue-team/sherlocks/optinseltrace-2>
- <https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html>
- <https://attack.mitre.org/techniques/T1078/004/>
