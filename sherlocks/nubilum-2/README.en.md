---
sherlock: Nubilum-2
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
state: Retired
evidence: CloudTrail from an account with an exposed S3 bucket
tools: [jq, Splunk, AWS CLI]
tags: [dfir, cloud, aws, s3, iam, cloudtrail]
---

# Nubilum-2 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; no platform answers.

## Scenario

Forela uses **S3** as storage and data lake. A user reports being unable to access files in one directory, and a **misconfigured bucket policy** on `forela-fileshare` is suspected. Reconstruct what the intruder did and why the legitimate user lost access.

## Evidence

- **CloudTrail** logs from account `949622803460`, gzipped JSON per region.

## Investigation

### 1. Prepare

```bash
jq -s '[.[].Records[]] | sort_by(.eventTime) | unique_by(.eventID)' CloudTrail/*/*.json > merged.json
jq -r '.[] | [.eventTime,.eventName,.userIdentity.type,.sourceIPAddress,.errorCode] | @tsv' merged.json | sort > timeline.tsv
```

### 2. The origin

The `userAgent` separates the attacker from normal traffic: a recent `aws-cli` from a pentest distribution marks the manual calls. That isolates the source IP and the window.

```bash
jq -r '.[] | "\(.sourceIPAddress)\t\(.userAgent)"' merged.json | sort -u | grep -i "aws-cli"
```

### 3. The initial leak

**Anonymous** reads (`userIdentity.type = AWSAccount`/`Anonymous`) of bucket objects: the attacker downloads an access-key CSV without authenticating. That is where everything starts.

```bash
jq -r '.[] | select(.eventName=="GetObject") | [.eventTime,.userIdentity.type,.requestParameters.key] | @tsv' merged.json | grep -i "accesskeys\|credential"
```

### 4. Escalation with the stolen keys

Using the CSV keys, the actor chains dozens of **denied** calls (`AccessDenied`) until finding a useful permission, and ends up writing an **inline policy on itself** to widen privileges.

```bash
jq -r '.[] | select(.errorCode=="AccessDenied") | .eventName' merged.json | sort | uniq -c | sort -rn
jq -r '.[] | select(.eventName|test("PutUserPolicy|AttachUserPolicy|CreateAccessKey|PutBucketPolicy")) | [.eventTime,.eventName,.userIdentity.arn] | @tsv' merged.json
```

### 5. Business impact

The legitimate user stops seeing their files because the objects end up encrypted with a KMS key they lack `kms:Decrypt` for. The `AccessDenied` on `kms:Decrypt` plus the ACL/policy changes explain the helpdesk ticket.

## Findings

- Entry: a publicly readable bucket with an IAM access-key CSV inside.
- Escalation: probing with `AccessDenied` until a policy-write permission appears.
- Persistence: an access key created and an inline policy self-assigned.
- Impact: the legitimate user loses access through policy and encryption changes.

## Lessons

- A public bucket holding credentials is an account compromise, not a data leak.
- `AccessDenied` events are evidence: they map the attacker's reconnaissance.
- `PutUserPolicy` on one's own user is quiet privilege escalation and deserves an alert.
- The helpdesk ticket is the tip: the policy change is the cause.

## Difficulty note

The index records **Medium**; one public source lists it as **Easy**. It stays Medium here and the discrepancy is noted.
