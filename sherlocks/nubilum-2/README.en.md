---
sherlock: Nubilum-2
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
evidence: CloudTrail from an account with an exposed S3 bucket
tools: [jq, Splunk, AWS CLI]
---

# Nubilum-2 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Forela uses **S3** as both storage and data lake. A user reports being unable to access files in one directory, and a **misconfigured bucket policy** on `forela-fileshare` is suspected of exposing objects publicly. Rebuild what the intruder did.

## Evidence

- The account's **CloudTrail** logs (many JSON files).

## Method

1. **Prepare**: ingest the JSON into a SIEM (Splunk/Elastic) or normalise with `jq`.

```bash
jq -r '[.eventTime,.eventName,.userIdentity.type,.userIdentity.arn,.sourceIPAddress,.errorCode]|@tsv' *.json \
  | sort > timeline.tsv
```

2. **Entry**: bucket policy and ACL changes (`PutBucketPolicy`, `PutBucketAcl`, `PutObjectAcl`) and who made them.

3. **Identity**: `CreateAccessKey` for an existing user — the classic persistence pattern — and from which IP.

4. **Object activity**: `ListObjects`, `GetObject`, `DeleteObject`; `AccessDenied` on `kms:Decrypt` explains why the legitimate user lost access.

5. **Wrap-up**: which objects were exposed or deleted, in which window, under which identity.

## What it teaches

- A permissive bucket policy makes internal data public without touching IAM.
- Creating an access key is quiet persistence in AWS.
- `AccessDenied` events are evidence too: they show business impact.
- Cloud analysis happens through queries, not by opening files one by one.

## Pitfalls

- **Encoding**: some exports wrap JSON in a single line or inside `Records[]`; unwrap first.
- **Duplicates**: log deliveries can repeat events; deduplicate on `eventID`.
- **`kms:Decrypt`**: without it, a "public" object still cannot be read.
